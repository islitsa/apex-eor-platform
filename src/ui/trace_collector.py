"""
Trace Collector - Captures Agent Execution with Real Reasoning

This module provides non-invasive instrumentation to capture agent execution,
including their actual Chain-of-Thought reasoning and planning steps.

Key Features:
- Captures real CoT output from UXDesigner
- Captures planning steps from GradioImplementationAgent
- Records knowledge queries to Pinecone
- Stores decisions and their reasoning
- Converts traces to human-readable conversation format
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum


class TraceType(Enum):
    """Types of trace events"""
    CALL = "call"  # Method was called
    THINKING = "thinking"  # Agent is processing (CoT, planning)
    DECISION = "decision"  # Agent made a decision
    KNOWLEDGE_QUERY = "knowledge_query"  # Queried Pinecone
    REASONING = "reasoning"  # Actual CoT/planning output
    ERROR = "error"  # Something went wrong


@dataclass
class ExecutionTrace:
    """
    Single trace event in agent execution

    Captures not just what happened, but WHY it happened
    by storing actual agent reasoning (CoT, planning)
    """
    timestamp: float
    agent: str
    method: str
    trace_type: TraceType
    data: Dict[str, Any] = field(default_factory=dict)

    # NEW: Actual agent reasoning
    reasoning: Optional[str] = None  # Real CoT output from agent
    knowledge_used: List[str] = field(default_factory=list)  # Pinecone results that influenced this

    def to_conversation(self) -> str:
        """Convert trace to human-readable format"""
        if self.trace_type == TraceType.CALL:
            return f"🎯 Calling {self.agent}.{self.method}"

        elif self.trace_type == TraceType.THINKING:
            thought = self.data.get('thought', 'Processing...')
            return f"💭 {self.agent}: {thought}"

        elif self.trace_type == TraceType.REASONING:
            # Show actual CoT reasoning
            if self.reasoning:
                # Truncate for display
                preview = self.reasoning[:200] + "..." if len(self.reasoning) > 200 else self.reasoning
                return f"🧠 {self.agent} Reasoning:\n{preview}"
            return f"🧠 {self.agent}: Applied reasoning"

        elif self.trace_type == TraceType.DECISION:
            decision = self.data.get('decision', 'Completed')
            return f"✅ {self.agent}: {decision}"

        elif self.trace_type == TraceType.KNOWLEDGE_QUERY:
            query = self.data.get('query', 'patterns')
            count = self.data.get('count', 0)
            return f"📚 {self.agent}: Queried Pinecone for '{query}' ({count} results)"

        elif self.trace_type == TraceType.ERROR:
            error = self.data.get('error', 'Unknown error')
            return f"❌ {self.agent}: Error - {error}"

        return f"{self.agent}: {self.trace_type.value}"

    def to_dict(self) -> Dict:
        """Serialize for storage"""
        return {
            'timestamp': self.timestamp,
            'agent': self.agent,
            'method': self.method,
            'trace_type': self.trace_type.value,
            'data': self.data,
            'reasoning': self.reasoning,
            'knowledge_used': self.knowledge_used
        }


class UniversalTraceCollector:
    """
    Collects execution traces from agents

    Two approaches:
    1. Auto-wrapping: Automatically wraps agent methods
    2. Explicit: Agents call trace_* methods directly

    We'll use explicit approach for more reliable reasoning capture
    """

    def __init__(self, stream_container=None):
        self.traces: List[ExecutionTrace] = []
        self.enabled = True
        self.stream_container = stream_container  # Streamlit container for live updates

    def clear(self):
        """Clear all traces"""
        self.traces = []

    def trace_call(self, agent: str, method: str, args_preview: str = ""):
        """Record a method call"""
        if not self.enabled:
            return

        trace = ExecutionTrace(
            timestamp=time.time(),
            agent=agent,
            method=method,
            trace_type=TraceType.CALL,
            data={'args': args_preview}
        )
        self.traces.append(trace)

    def trace_thinking(self, agent: str, method: str, thought: str):
        """Record agent thinking/processing"""
        if not self.enabled:
            return

        trace = ExecutionTrace(
            timestamp=time.time(),
            agent=agent,
            method=method,
            trace_type=TraceType.THINKING,
            data={'thought': thought}
        )
        self.traces.append(trace)

    def trace_reasoning(self, agent: str, method: str, reasoning: str, knowledge_used: List[str] = None):
        """
        Record actual agent reasoning (CoT, planning)

        This is the key enhancement - we capture REAL reasoning,
        not just generic messages
        """
        if not self.enabled:
            return

        trace = ExecutionTrace(
            timestamp=time.time(),
            agent=agent,
            method=method,
            trace_type=TraceType.REASONING,
            reasoning=reasoning,
            knowledge_used=knowledge_used or []
        )
        self.traces.append(trace)

        # Stream to UI if container available
        if self.stream_container:
            try:
                import streamlit as st
                with self.stream_container:
                    st.markdown(f"**🧠 {agent}** - {method}")
                    # Show full reasoning in expandable text area
                    with st.expander("View Full Reasoning", expanded=True):
                        st.text_area(
                            "Reasoning",
                            reasoning,
                            height=400,
                            disabled=True,
                            label_visibility="collapsed"
                        )
                    if knowledge_used:
                        st.caption(f"📚 Knowledge: {', '.join(knowledge_used[:3])}")
                    st.divider()
            except:
                pass  # Silently fail if streaming doesn't work

    def trace_knowledge_query(self, agent: str, query: str, result_count: int, results_preview: List[str] = None):
        """Record Pinecone knowledge query"""
        if not self.enabled:
            return

        trace = ExecutionTrace(
            timestamp=time.time(),
            agent=agent,
            method="query_knowledge",
            trace_type=TraceType.KNOWLEDGE_QUERY,
            data={
                'query': query,
                'count': result_count
            },
            knowledge_used=results_preview or []
        )
        self.traces.append(trace)

    def trace_decision(self, agent: str, method: str, decision: str, details: str = ""):
        """Record a decision made by agent"""
        if not self.enabled:
            return

        trace = ExecutionTrace(
            timestamp=time.time(),
            agent=agent,
            method=method,
            trace_type=TraceType.DECISION,
            data={
                'decision': decision,
                'details': details[:500]  # Truncate details
            }
        )
        self.traces.append(trace)

    def trace_error(self, agent: str, method: str, error: str):
        """Record an error"""
        if not self.enabled:
            return

        trace = ExecutionTrace(
            timestamp=time.time(),
            agent=agent,
            method=method,
            trace_type=TraceType.ERROR,
            data={'error': str(error)}
        )
        self.traces.append(trace)

    def get_traces_for_agent(self, agent: str) -> List[ExecutionTrace]:
        """Get all traces for a specific agent"""
        return [t for t in self.traces if t.agent == agent]

    def get_reasoning_traces(self) -> List[ExecutionTrace]:
        """Get all reasoning traces (CoT, planning)"""
        return [t for t in self.traces if t.trace_type == TraceType.REASONING]

    def get_knowledge_queries(self) -> List[ExecutionTrace]:
        """Get all Pinecone knowledge queries"""
        return [t for t in self.traces if t.trace_type == TraceType.KNOWLEDGE_QUERY]

    def replay_as_conversation(self) -> List[str]:
        """Convert all traces to conversation format"""
        return [trace.to_conversation() for trace in self.traces]

    def export_to_dict(self) -> Dict:
        """Export all traces for storage"""
        return {
            'traces': [t.to_dict() for t in self.traces],
            'total_count': len(self.traces),
            'agent_breakdown': self._get_agent_breakdown()
        }

    def _get_agent_breakdown(self) -> Dict[str, int]:
        """Count traces per agent"""
        breakdown = {}
        for trace in self.traces:
            breakdown[trace.agent] = breakdown.get(trace.agent, 0) + 1
        return breakdown

    def ask_question(self, question: str) -> Dict[str, str]:
        """
        Search traces to answer questions about design decisions (0 tokens)

        Args:
            question: User question about design/implementation

        Returns:
            Dict mapping agent name to answer string
        """
        answers = {}
        question_lower = question.lower()
        question_words = set(question_lower.split())

        # Search reasoning traces from all agents
        reasoning_traces = self.get_reasoning_traces()

        for trace in reasoning_traces:
            if not trace.reasoning:
                continue

            # Check if reasoning mentions relevant keywords from question
            reasoning_lower = trace.reasoning.lower()

            # Calculate relevance score
            matches = sum(1 for word in question_words if len(word) > 3 and word in reasoning_lower)

            if matches >= 2:  # At least 2 significant word matches
                # Extract relevant section (first 300 chars with match)
                answer = trace.reasoning

                # Add to answers (one answer per agent)
                if trace.agent not in answers:
                    answers[trace.agent] = answer
                elif matches > sum(1 for word in question_words if word in answers[trace.agent].lower()):
                    # Replace if this trace is more relevant
                    answers[trace.agent] = answer

        return answers

    def get_design_patterns_used(self) -> List[str]:
        """Get list of design patterns that were used"""
        patterns = []
        for trace in self.traces:
            if trace.knowledge_used:
                patterns.extend(trace.knowledge_used)
        return list(set(patterns))  # Unique patterns
