from langgraph.graph import StateGraph, END
from proofreader.agent.state import AgentState
from proofreader.agent.nodes.style import analyze_style
from proofreader.agent.nodes.typos import correct_typos
from proofreader.agent.nodes.structure import improve_structure
from proofreader.agent.nodes.coherence import check_coherence

def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("style_analysis", analyze_style)
    workflow.add_node("typo_correction", correct_typos)
    workflow.add_node("structure_improvement", improve_structure)
    workflow.add_node("coherence_check", check_coherence)
    
    # Define edges
    # style -> typos -> structure -> coherence -> end
    workflow.set_entry_point("style_analysis")
    
    workflow.add_edge("style_analysis", "typo_correction")
    workflow.add_edge("typo_correction", "structure_improvement")
    workflow.add_edge("structure_improvement", "coherence_check")
    workflow.add_edge("coherence_check", END)
    
    return workflow.compile()
