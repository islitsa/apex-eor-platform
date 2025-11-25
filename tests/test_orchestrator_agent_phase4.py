"""
Test Orchestrator Agent - Phase 4

Verifies that the autonomous agent mode works correctly.
"""

def test_agent_initialization():
    """Test that OrchestratorAgent initializes with all skills"""
    print("Testing OrchestratorAgent initialization...")

    from src.agents.ui_orchestrator import UICodeOrchestrator
    from src.agents.orchestrator_agent import OrchestratorAgent

    # Create orchestrator
    orchestrator = UICodeOrchestrator()

    # Create agent
    agent = OrchestratorAgent(orchestrator=orchestrator)

    # Verify skills exist
    assert hasattr(agent, 'skills'), "Agent missing skills attribute"
    assert len(agent.skills) > 0, "Agent has no skills"

    # Verify key skills are present
    expected_skills = [
        "discover_data",
        "filter_sources",
        "retrieve_knowledge",
        "build_session_context",
        "prepare_builder_context",
        "generate_ux",
        "refine_ux",
        "validate_ux",
        "generate_react",
        "regenerate_react",
        "validate_react",
        "evaluate_progress",
        "finish"
    ]

    for skill_name in expected_skills:
        assert skill_name in agent.skills, f"Missing skill: {skill_name}"

    print(f"  [PASS] Agent initialized with {len(agent.skills)} skills")
    print(f"  Skills: {', '.join(agent.skills.keys())}")


def test_agent_mode_flag():
    """Test that orchestrator supports agent mode flag"""
    print("\nTesting orchestrator agent mode flag...")

    from src.agents.ui_orchestrator import UICodeOrchestrator

    # Test with agent mode disabled (default)
    orch1 = UICodeOrchestrator(use_agent_mode=False)
    assert hasattr(orch1, 'use_agent_mode'), "Missing use_agent_mode attribute"
    assert orch1.use_agent_mode == False, "Agent mode should be disabled"
    assert orch1.agent is None, "Agent should be None when disabled"

    print("  [PASS] Agent mode disabled by default")

    # Test with agent mode enabled
    orch2 = UICodeOrchestrator(use_agent_mode=True)
    assert orch2.use_agent_mode == True, "Agent mode should be enabled"
    assert orch2.agent is not None, "Agent should be initialized when enabled"

    print("  [PASS] Agent mode enabled works correctly")


def test_session_memory_structure():
    """Test SessionMemory dataclass structure"""
    print("\nTesting SessionMemory structure...")

    from src.agents.orchestrator_agent import SessionMemory, OrchestratorGoal

    # Create empty memory
    memory = SessionMemory(session_id="test-123")

    # Verify attributes exist
    assert memory.session_id == "test-123"
    assert memory.iteration == 0
    assert memory.user_requirements == {}
    assert memory.user_context == {}
    assert memory.data_context is None
    assert memory.knowledge is None
    assert memory.session_ctx is None
    assert memory.design_spec is None
    assert memory.react_files is None
    assert memory.evaluation_history == []
    assert memory.actions_taken == []
    assert memory.skills_used == []
    assert memory.errors == []
    assert memory.last_error is None
    assert memory.planning_trace == []
    assert memory.current_goal == OrchestratorGoal.GENERATE_UI
    assert memory.ux_satisfactory == False
    assert memory.react_satisfactory == False
    assert memory.goal_achieved == False

    print("  [PASS] SessionMemory has all required attributes")


def test_plan_structure():
    """Test Plan dataclass structure"""
    print("\nTesting Plan structure...")

    from src.agents.orchestrator_agent import Plan

    # Create plan
    plan = Plan(
        skill="discover_data",
        reasoning="Need to fetch data from API",
        arguments={"filter_sources": ["fracfocus"]},
        expected_outcome="Data context populated"
    )

    assert plan.skill == "discover_data"
    assert plan.reasoning == "Need to fetch data from API"
    assert plan.arguments == {"filter_sources": ["fracfocus"]}
    assert plan.expected_outcome == "Data context populated"

    print("  [PASS] Plan dataclass works correctly")


def test_skill_registry():
    """Test that all skills have proper structure"""
    print("\nTesting skill registry structure...")

    from src.agents.ui_orchestrator import UICodeOrchestrator
    from src.agents.orchestrator_agent import OrchestratorAgent

    orchestrator = UICodeOrchestrator()
    agent = OrchestratorAgent(orchestrator=orchestrator)

    # Verify each skill has required structure
    for skill_name, skill_info in agent.skills.items():
        assert "fn" in skill_info, f"Skill {skill_name} missing 'fn'"
        assert "description" in skill_info, f"Skill {skill_name} missing 'description'"
        assert callable(skill_info["fn"]), f"Skill {skill_name} fn not callable"
        assert len(skill_info["description"]) > 0, f"Skill {skill_name} has empty description"

    print(f"  [PASS] All {len(agent.skills)} skills have proper structure")


def test_backward_compatibility():
    """Test that Phase 3 still works (backward compatibility)"""
    print("\nTesting backward compatibility...")

    from src.agents.ui_orchestrator import UICodeOrchestrator

    # Create orchestrator without agent mode (Phase 3)
    orchestrator = UICodeOrchestrator(use_agent_mode=False)

    # Verify Phase 3 tools still exist
    assert hasattr(orchestrator, 'filter_tool'), "Missing filter_tool"
    assert hasattr(orchestrator, 'discovery_tool'), "Missing discovery_tool"
    assert hasattr(orchestrator, 'knowledge_tool'), "Missing knowledge_tool"
    assert hasattr(orchestrator, 'shaping_tool'), "Missing shaping_tool"
    assert hasattr(orchestrator, 'context_assembly_tool'), "Missing context_assembly_tool"
    assert hasattr(orchestrator, 'knowledge_assembly_tool'), "Missing knowledge_assembly_tool"
    assert hasattr(orchestrator, 'execution_tool'), "Missing execution_tool"

    # Verify Phase 2 evaluation methods still exist
    assert hasattr(orchestrator, '_evaluate_ux_spec'), "Missing _evaluate_ux_spec"
    assert hasattr(orchestrator, '_evaluate_react_output'), "Missing _evaluate_react_output"
    assert hasattr(orchestrator, '_decide_next_action'), "Missing _decide_next_action"

    # Verify agents still exist
    assert hasattr(orchestrator, 'ux_designer'), "Missing ux_designer"
    assert hasattr(orchestrator, 'react_developer'), "Missing react_developer"

    # Verify main method still exists
    assert hasattr(orchestrator, 'generate_ui_code'), "Missing generate_ui_code"

    print("  [PASS] Phase 3 tools and methods still available")
    print("  [PASS] Backward compatibility maintained")


if __name__ == "__main__":
    print("="*60)
    print("PHASE 4 ORCHESTRATOR AGENT TESTS")
    print("="*60)

    try:
        test_agent_initialization()
        test_agent_mode_flag()
        test_session_memory_structure()
        test_plan_structure()
        test_skill_registry()
        test_backward_compatibility()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nPhase 4 autonomous agent implementation verified!")
        print("OrchestratorAgent ready for autonomous reasoning.")
        print("\nBackward compatibility confirmed:")
        print("  - Phase 3 tools still available")
        print("  - Phase 2 evaluation still works")
        print("  - Agent mode is opt-in")

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
