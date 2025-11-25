"""
Test SharedSessionMemory - Phase 5 Step 1

Verifies that the communication bus for multi-agent collaboration works correctly.
"""

def test_shared_memory_initialization():
    """Test SharedSessionMemory initializes correctly"""
    print("Testing SharedSessionMemory initialization...")

    from src.agents.shared_memory import SharedSessionMemory

    memory = SharedSessionMemory(session_id="test-session-1")

    # Verify basic attributes
    assert memory.session_id == "test-session-1"
    assert memory.iteration == 0
    assert memory.user_requirements == {}
    assert memory.user_context == {}
    assert memory.data_context is None
    assert memory.knowledge is None
    assert memory.session_ctx is None

    # Verify UX attributes
    assert memory.ux_spec is None
    assert memory.ux_spec_version == 0
    assert memory.ux_history == []
    assert memory.ux_reasoning_trace == []

    # Verify React attributes
    assert memory.react_files is None
    assert memory.react_version == 0
    assert memory.react_history == []
    assert memory.react_reasoning_trace == []

    # Verify conflict tracking
    assert memory.design_conflicts == []
    assert memory.implementation_conflicts == []
    assert memory.resolved_conflicts == []

    # Verify questions
    assert memory.questions == []
    assert memory.unanswered_questions == []

    # Verify status
    assert memory.ux_status == "idle"
    assert memory.react_status == "idle"
    assert memory.orchestrator_status == "idle"

    # Verify success flags
    assert memory.ux_satisfactory == False
    assert memory.react_satisfactory == False
    assert memory.goal_achieved == False

    # Verify negotiation log
    assert memory.negotiation_log == []

    print("  [PASS] SharedSessionMemory initialized correctly")


def test_conflict_management():
    """Test conflict tracking and resolution"""
    print("\nTesting conflict management...")

    from src.agents.shared_memory import SharedSessionMemory, Conflict, ConflictType

    memory = SharedSessionMemory(session_id="test-session-2")

    # Create a design conflict
    design_conflict = Conflict(
        conflict_type=ConflictType.DESIGN_SCHEMA_MISMATCH,
        source_agent="UX Designer",
        description="Missing required field 'id' in component schema",
        affected_component="PipelineCard",
        suggested_resolution="Add 'id' field to component",
        severity="high"
    )

    # Add design conflict
    memory.add_conflict(design_conflict, is_design=True)

    assert len(memory.design_conflicts) == 1
    assert len(memory.implementation_conflicts) == 0
    assert design_conflict in memory.design_conflicts

    print("  [PASS] Design conflict added successfully")

    # Create an implementation conflict
    impl_conflict = Conflict(
        conflict_type=ConflictType.IMPLEMENTATION_TYPE_ERROR,
        source_agent="React Developer",
        description="Type error: 'data' prop expected array, got object",
        affected_component="DataTable",
        suggested_resolution="Change data type to array",
        severity="critical"
    )

    # Add implementation conflict
    memory.add_conflict(impl_conflict, is_design=False)

    assert len(memory.design_conflicts) == 1
    assert len(memory.implementation_conflicts) == 1
    assert impl_conflict in memory.implementation_conflicts

    print("  [PASS] Implementation conflict added successfully")

    # Resolve a conflict
    memory.resolve_conflict(design_conflict)

    assert len(memory.design_conflicts) == 0
    assert len(memory.resolved_conflicts) == 1
    assert design_conflict in memory.resolved_conflicts

    print("  [PASS] Conflict resolved successfully")

    # Get unresolved conflicts
    unresolved = memory.get_unresolved_conflicts(is_design=False)
    assert len(unresolved) == 1
    assert impl_conflict in unresolved

    print("  [PASS] Unresolved conflicts retrieved correctly")


def test_question_system():
    """Test inter-agent question system"""
    print("\nTesting inter-agent question system...")

    from src.agents.shared_memory import SharedSessionMemory

    memory = SharedSessionMemory(session_id="test-session-3")

    # React asks UX a question
    memory.ask_question(
        asking_agent="React Developer",
        target_agent="UX Designer",
        question="Should the PipelineCard component be collapsible?",
        context={"component": "PipelineCard", "reason": "better UX"}
    )

    assert len(memory.questions) == 1
    assert len(memory.unanswered_questions) == 1

    question = memory.questions[0]
    assert question.asking_agent == "React Developer"
    assert question.target_agent == "UX Designer"
    assert question.question == "Should the PipelineCard component be collapsible?"
    assert question.answered == False

    print("  [PASS] Question asked successfully")

    # UX gets questions for itself
    ux_questions = memory.get_questions_for_agent("UX Designer")
    assert len(ux_questions) == 1
    assert ux_questions[0] == question

    print("  [PASS] Questions for agent retrieved correctly")

    # UX answers the question
    memory.answer_question(question, "Yes, all cards should be collapsible for better space management")

    assert question.answered == True
    assert question.answer == "Yes, all cards should be collapsible for better space management"
    assert len(memory.unanswered_questions) == 0

    print("  [PASS] Question answered successfully")


def test_ux_spec_updates():
    """Test UX spec version tracking"""
    print("\nTesting UX spec version tracking...")

    from src.agents.shared_memory import SharedSessionMemory

    memory = SharedSessionMemory(session_id="test-session-4")

    # Mock DesignSpec
    class MockDesignSpec:
        def __init__(self, version):
            self.version = version
            self.components = ["Header", "DataTable"]

    # Initial spec
    spec_v1 = MockDesignSpec(1)
    memory.update_ux_spec(spec_v1, reasoning="Initial design generated")

    assert memory.ux_spec == spec_v1
    assert memory.ux_spec_version == 1
    assert len(memory.ux_history) == 1
    assert memory.ux_history[0]["version"] == 1
    assert memory.ux_history[0]["spec"] == spec_v1

    print("  [PASS] UX spec v1 updated")

    # Refined spec
    spec_v2 = MockDesignSpec(2)
    memory.update_ux_spec(spec_v2, reasoning="Added FilterPanel component")

    assert memory.ux_spec == spec_v2
    assert memory.ux_spec_version == 2
    assert len(memory.ux_history) == 2
    assert memory.ux_history[1]["version"] == 2

    print("  [PASS] UX spec v2 updated (refinement)")

    # Version should increment automatically
    spec_v3 = MockDesignSpec(3)
    memory.update_ux_spec(spec_v3, reasoning="Fixed schema mismatch")

    assert memory.ux_spec_version == 3
    assert len(memory.ux_history) == 3

    print("  [PASS] UX spec version tracking works correctly")


def test_react_files_updates():
    """Test React files version tracking"""
    print("\nTesting React files version tracking...")

    from src.agents.shared_memory import SharedSessionMemory

    memory = SharedSessionMemory(session_id="test-session-5")

    # Initial implementation
    files_v1 = {
        "App.tsx": "import React from 'react';\nexport default function App() { return <div>v1</div>; }"
    }
    memory.update_react_files(files_v1, reasoning="Initial implementation generated")

    assert memory.react_files == files_v1
    assert memory.react_version == 1
    assert len(memory.react_history) == 1

    print("  [PASS] React files v1 updated")

    # Fixed version
    files_v2 = {
        "App.tsx": "import React from 'react';\nexport default function App() { return <div>v2</div>; }"
    }
    memory.update_react_files(files_v2, reasoning="Fixed type errors")

    assert memory.react_files == files_v2
    assert memory.react_version == 2
    assert len(memory.react_history) == 2

    print("  [PASS] React files v2 updated (bug fix)")

    # Regenerated component
    files_v3 = {
        "App.tsx": "import React from 'react';\nexport default function App() { return <div>v3</div>; }",
        "FilterPanel.tsx": "export function FilterPanel() { return <div>Filters</div>; }"
    }
    memory.update_react_files(files_v3, reasoning="Added FilterPanel component")

    assert memory.react_version == 3
    assert len(memory.react_history) == 3
    assert "FilterPanel.tsx" in files_v3

    print("  [PASS] React files version tracking works correctly")


def test_negotiation_log():
    """Test multi-agent negotiation logging"""
    print("\nTesting negotiation log...")

    from src.agents.shared_memory import SharedSessionMemory

    memory = SharedSessionMemory(session_id="test-session-6")

    # Log negotiation messages
    memory.log_negotiation(
        from_agent="Orchestrator",
        to_agent="UX Designer",
        message="Please generate initial design spec",
        metadata={"priority": "high"}
    )

    memory.log_negotiation(
        from_agent="UX Designer",
        to_agent="React Developer",
        message="Design spec ready, please implement",
        metadata={"spec_version": 1}
    )

    memory.log_negotiation(
        from_agent="React Developer",
        to_agent="UX Designer",
        message="Type error detected in component schema",
        metadata={"component": "PipelineCard", "error": "missing id field"}
    )

    assert len(memory.negotiation_log) == 3

    # Verify log entries
    log1 = memory.negotiation_log[0]
    assert log1["from"] == "Orchestrator"
    assert log1["to"] == "UX Designer"
    assert "Please generate" in log1["message"]

    log2 = memory.negotiation_log[1]
    assert log2["from"] == "UX Designer"
    assert log2["to"] == "React Developer"

    log3 = memory.negotiation_log[2]
    assert log3["from"] == "React Developer"
    assert log3["to"] == "UX Designer"
    assert "Type error" in log3["message"]

    print("  [PASS] Negotiation log working correctly")


def test_state_summary():
    """Test state summary for agent planning"""
    print("\nTesting state summary...")

    from src.agents.shared_memory import SharedSessionMemory

    memory = SharedSessionMemory(session_id="test-session-7")

    # Initial state
    summary = memory.get_current_state_summary()

    assert summary["iteration"] == 0
    assert summary["has_data"] == False
    assert summary["has_knowledge"] == False
    assert summary["has_ux_spec"] == False
    assert summary["has_react_files"] == False
    assert summary["ux_version"] == 0
    assert summary["react_version"] == 0

    print("  [PASS] Initial state summary correct")

    # Add some data
    memory.data_context = {"success": True, "pipelines": []}
    memory.knowledge = {"ux_patterns": {}}

    summary = memory.get_current_state_summary()
    assert summary["has_data"] == True
    assert summary["has_knowledge"] == True

    print("  [PASS] State summary updates with data")

    # Add UX spec
    memory.update_ux_spec({"components": []}, "test")

    summary = memory.get_current_state_summary()
    assert summary["has_ux_spec"] == True
    assert summary["ux_version"] == 1

    print("  [PASS] State summary updates with UX spec")

    # Add React files
    memory.update_react_files({"App.tsx": "test"}, "test")

    summary = memory.get_current_state_summary()
    assert summary["has_react_files"] == True
    assert summary["react_version"] == 1

    print("  [PASS] State summary updates with React files")


def test_conflict_types():
    """Test all conflict types are defined"""
    print("\nTesting conflict types...")

    from src.agents.shared_memory import ConflictType

    expected_types = [
        "DESIGN_SCHEMA_MISMATCH",
        "MISSING_DESIGN_FIELD",
        "IMPLEMENTATION_TYPE_ERROR",
        "INVALID_IMPORT",
        "MISSING_COMPONENT",
        "DATA_SOURCE_MISMATCH",
        "STAGE_MISMATCH",
        "FILE_PATH_ERROR"
    ]

    for type_name in expected_types:
        assert hasattr(ConflictType, type_name), f"Missing conflict type: {type_name}"

    print(f"  [PASS] All {len(expected_types)} conflict types defined")


if __name__ == "__main__":
    print("="*60)
    print("SHARED SESSION MEMORY TESTS (Phase 5 Step 1)")
    print("="*60)

    try:
        test_shared_memory_initialization()
        test_conflict_management()
        test_question_system()
        test_ux_spec_updates()
        test_react_files_updates()
        test_negotiation_log()
        test_state_summary()
        test_conflict_types()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nSharedSessionMemory is working correctly!")
        print("\nVerified capabilities:")
        print("  [OK] Conflict tracking (design + implementation)")
        print("  [OK] Question system (inter-agent)")
        print("  [OK] Version tracking (UX spec + React files)")
        print("  [OK] Negotiation log (audit trail)")
        print("  [OK] State summary (for agent planning)")
        print("  [OK] All conflict types defined")
        print("\nPhase 5 Step 1 foundation is solid!")
        print("Ready to proceed with Step 2 (UX Agent upgrade)")

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
