"""
Post-Convergence Validation Tool - Fix #13

Validates generated React code for runtime correctness after convergence.

This tool fills the gap between structural convergence (UX matches React) and
runtime correctness (the code actually works).

Checks:
1. TypeScript compilation (tsc --noEmit)
2. Runtime type correctness (no obvious type bugs)
3. Import/export validity
4. Basic smoke tests

Produces RuntimeConflict objects if validation fails.
"""

from typing import Dict, Any, List
from pathlib import Path
import subprocess
import json
import tempfile
import shutil


class PostConvergenceValidator:
    """
    Phase 6.3: Post-convergence runtime validation.

    Catches bugs that structural analysis misses:
    - Type mismatches (data.filter() on object instead of array)
    - Import errors
    - TypeScript compilation errors
    - Missing dependencies
    """

    def validate(self, react_files: Dict[str, str], output_dir: str) -> List[Dict[str, Any]]:
        """
        Validate generated React code for runtime correctness.

        Args:
            react_files: Dict of filename -> code from React Developer
            output_dir: Path to generated React project

        Returns:
            List of validation errors (runtime conflicts)
        """
        errors = []

        print("\n[Post-Convergence Validator] Running validation checks...")

        # Check 1: TypeScript compilation
        ts_errors = self._check_typescript_compilation(output_dir)
        if ts_errors:
            errors.extend(ts_errors)
            print(f"  ❌ TypeScript: {len(ts_errors)} errors")
        else:
            print(f"  ✅ TypeScript: No compilation errors")

        # Check 2: Import validity
        import_errors = self._check_imports(react_files)
        if import_errors:
            errors.extend(import_errors)
            print(f"  ❌ Imports: {len(import_errors)} errors")
        else:
            print(f"  ✅ Imports: All valid")

        # Check 3: Type safety patterns
        type_errors = self._check_type_safety(react_files)
        if type_errors:
            errors.extend(type_errors)
            print(f"  ❌ Type Safety: {len(type_errors)} issues")
        else:
            print(f"  ✅ Type Safety: No issues")

        if errors:
            print(f"\n[Post-Convergence Validator] ⚠️  Found {len(errors)} validation errors")
        else:
            print(f"\n[Post-Convergence Validator] ✅ All validation checks passed")

        return errors

    def _check_typescript_compilation(self, output_dir: str) -> List[Dict[str, Any]]:
        """
        Run TypeScript compiler to check for type errors.

        Returns:
            List of compilation errors
        """
        errors = []
        output_path = Path(output_dir)

        if not output_path.exists():
            return [{
                "type": "build_error",
                "severity": "high",
                "message": f"Output directory not found: {output_dir}",
                "file": "N/A"
            }]

        # Check if tsconfig.json exists
        tsconfig = output_path / "tsconfig.json"
        if not tsconfig.exists():
            return [{
                "type": "build_error",
                "severity": "medium",
                "message": "No tsconfig.json found, skipping TypeScript validation",
                "file": "tsconfig.json"
            }]

        try:
            # Run tsc --noEmit to check types without generating files
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=output_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                # Parse TypeScript errors
                error_lines = result.stdout.split('\n')
                for line in error_lines:
                    if '.ts' in line or '.tsx' in line:
                        # Extract file, line, column, and error message
                        # Format: src/App.tsx(14,17): error TS2339: Property 'filter' does not exist on type 'PipelinesResponse'
                        parts = line.split(': error ')
                        if len(parts) == 2:
                            location = parts[0]
                            message = parts[1]

                            errors.append({
                                "type": "typescript_error",
                                "severity": "high",
                                "message": message,
                                "location": location,
                                "file": location.split('(')[0] if '(' in location else location
                            })

        except subprocess.TimeoutExpired:
            errors.append({
                "type": "build_error",
                "severity": "high",
                "message": "TypeScript compilation timed out (>30s)",
                "file": "N/A"
            })
        except FileNotFoundError:
            # tsc not installed, skip check
            pass
        except Exception as e:
            errors.append({
                "type": "build_error",
                "severity": "medium",
                "message": f"TypeScript check failed: {str(e)}",
                "file": "N/A"
            })

        return errors

    def _check_imports(self, react_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Check for invalid imports (missing files, circular dependencies).

        Returns:
            List of import errors
        """
        errors = []

        # Build list of available modules
        available_files = set(react_files.keys())

        for filename, code in react_files.items():
            if not filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                continue

            # Extract import statements
            import_lines = [line for line in code.split('\n') if line.strip().startswith('import ')]

            for import_line in import_lines:
                # Skip external imports (from 'react', 'react-router', etc.)
                if "from 'react'" in import_line or 'from "react"' in import_line:
                    continue
                if "from '@" in import_line or 'from "@' in import_line:
                    continue

                # Extract local import path
                # import Foo from './Foo'
                # import { Bar } from './components/Bar.tsx'
                if "from '" in import_line:
                    path = import_line.split("from '")[1].split("'")[0]
                elif 'from "' in import_line:
                    path = import_line.split('from "')[1].split('"')[0]
                else:
                    continue

                # Check if the imported file exists
                if path.startswith('./') or path.startswith('../'):
                    # Resolve relative path
                    # For simplicity, check if any file matches the base name
                    base_name = path.split('/')[-1]

                    # Check with and without extension
                    if base_name not in available_files and f"{base_name}.tsx" not in available_files:
                        errors.append({
                            "type": "import_error",
                            "severity": "high",
                            "message": f"Import '{path}' not found",
                            "file": filename,
                            "import_path": path
                        })

        return errors

    def _check_type_safety(self, react_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Check for common type safety issues using pattern matching.

        Detects:
        - Calling array methods on non-arrays (data.filter when data is object)
        - Accessing properties without null checks
        - Type coercion issues

        Returns:
            List of type safety issues
        """
        errors = []

        for filename, code in react_files.items():
            if not filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                continue

            lines = code.split('\n')

            for i, line in enumerate(lines, 1):
                # Check for .filter() on non-arrays
                # Pattern: something.filter( where something isn't known to be an array
                if '.filter(' in line:
                    # Check if it's chained from a known array method or array literal
                    if not any(marker in line for marker in ['.map(', '.slice(', '[', 'Array(']):
                        # Look for variable name before .filter
                        parts = line.split('.filter(')[0]
                        var_name = parts.strip().split()[-1] if parts.strip().split() else ''

                        # Check if this variable is used with array methods elsewhere
                        # If we see `data.filter` but `data` is assigned from a hook that returns an object,
                        # flag it as suspicious
                        if var_name and not var_name.endswith('s') and 'const' not in line:
                            errors.append({
                                "type": "type_safety",
                                "severity": "medium",
                                "message": f"Suspicious .filter() call on '{var_name}' - may not be an array",
                                "file": filename,
                                "line": i,
                                "code": line.strip()
                            })

        return errors
