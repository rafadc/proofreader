from langgraph.graph import StateGraph, END
from blog_editor.agent.state import AgentState
from blog_editor.agent.nodes.style import analyze_style
from blog_editor.agent.nodes.typos import correct_typos
from blog_editor.agent.nodes.structure import improve_structure
from blog_editor.agent.nodes.coherence import check_coherence

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
