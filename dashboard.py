"""
Knowledge Graph Visualization Dashboard
Run: uv run streamlit run dashboard.py
"""
import streamlit as st
from src.energy_kg.neo4j_graph import Neo4jKnowledgeGraph
import streamlit.components.v1 as components


# Color scheme for entity types
COLORS = {
    "Market": "#e74c3c",      # Red
    "Hub": "#3498db",         # Blue
    "LoadZone": "#9b59b6",    # Purple
    "PowerPlant": "#2ecc71",  # Green
    "FuelType": "#f39c12",    # Orange
    "Region": "#1abc9c",      # Teal
}


def get_graph_data(kg: Neo4jKnowledgeGraph) -> tuple[list, list]:
    """Fetch all nodes and relationships from Neo4j"""
    with kg.driver.session() as session:
        # Get all nodes
        nodes_result = session.run("""
            MATCH (n:Entity)
            RETURN n.name AS name, n.type AS type, 
                   n.capacity_mw AS capacity, n.renewable AS renewable
        """)
        nodes = [dict(record) for record in nodes_result]
        
        # Get all relationships
        rels_result = session.run("""
            MATCH (a:Entity)-[r]->(b:Entity)
            RETURN a.name AS source, b.name AS target, type(r) AS relationship
        """)
        relationships = [dict(record) for record in rels_result]
        
    return nodes, relationships


def create_vis_js_html(nodes: list, relationships: list) -> str:
    """Create HTML with vis.js for graph visualization"""
    
    # Build nodes JSON
    vis_nodes = []
    for node in nodes:
        color = COLORS.get(node["type"], "#95a5a6")
        title = f"{node['name']}\\nType: {node['type']}"
        if node.get("capacity"):
            title += f"\\nCapacity: {node['capacity']} MW"
        
        vis_nodes.append({
            "id": node["name"],
            "label": node["name"],
            "color": color,
            "title": title,
            "size": 30 if node["type"] == "Market" else 20
        })
    
    # Build edges JSON
    vis_edges = []
    for rel in relationships:
        vis_edges.append({
            "from": rel["source"],
            "to": rel["target"],
            "label": rel["relationship"],
            "arrows": "to"
        })
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            #graph {{
                width: 100%;
                height: 550px;
                border: 1px solid #444;
                background-color: #1a1a1a;
            }}
        </style>
    </head>
    <body style="margin:0; background-color: #1a1a1a;">
        <div id="graph"></div>
        <script>
            var nodes = new vis.DataSet({vis_nodes});
            var edges = new vis.DataSet({vis_edges});
            
            var container = document.getElementById('graph');
            var data = {{ nodes: nodes, edges: edges }};
            var options = {{
                nodes: {{
                    shape: 'dot',
                    font: {{ color: '#ffffff', size: 12 }}
                }},
                edges: {{
                    color: {{ color: '#888888' }},
                    font: {{ color: '#aaaaaa', size: 10, background: '#1a1a1a' }},
                    smooth: {{ type: 'continuous' }}
                }},
                physics: {{
                    forceAtlas2Based: {{
                        gravitationalConstant: -30,
                        centralGravity: 0.005,
                        springLength: 150
                    }},
                    solver: 'forceAtlas2Based'
                }}
            }};
            
            var network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
    return html


def main():
    st.set_page_config(page_title="Energy Knowledge Graph", layout="wide")
    
    st.title("⚡ Energy Knowledge Graph Dashboard")
    
    # Connect to Neo4j
    try:
        kg = Neo4jKnowledgeGraph(uri="bolt://localhost:7687")
        st.success("✓ Connected to Neo4j")
    except Exception as e:
        st.error(f"Failed to connect to Neo4j: {e}")
        st.info("Make sure Neo4j is running: docker start neo4j")
        return
    
    # Sidebar - Statistics
    st.sidebar.header("📊 Graph Statistics")
    
    nodes, relationships = get_graph_data(kg)
    
    # Count by type
    type_counts = {}
    for node in nodes:
        t = node["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    
    st.sidebar.metric("Total Nodes", len(nodes))
    st.sidebar.metric("Total Relationships", len(relationships))
    
    st.sidebar.subheader("Nodes by Type")
    for t, count in sorted(type_counts.items()):
        color = COLORS.get(t, "#95a5a6")
        st.sidebar.markdown(f"<span style='color:{color}'>●</span> {t}: **{count}**", unsafe_allow_html=True)
    
    # Main content - Tabs
    tab1, tab2, tab3 = st.tabs(["🔗 Graph View", "📈 Analytics", "🔍 Query"])
    
    # Tab 1: Graph Visualization
    with tab1:
        st.subheader("Interactive Graph")
        st.caption("Drag nodes to rearrange. Scroll to zoom. Hover for details.")
        
        if nodes:
            html_content = create_vis_js_html(nodes, relationships)
            components.html(html_content, height=600)
        else:
            st.warning("No data in the graph")
    
    # Tab 2: Analytics
    with tab2:
        st.subheader("Capacity Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Capacity by Fuel Type**")
            with kg.driver.session() as session:
                result = session.run("""
                    MATCH (p:Entity {type: 'PowerPlant'})-[:USES_FUEL]->(f)
                    RETURN f.name AS fuel, sum(p.capacity_mw) AS capacity
                    ORDER BY capacity DESC
                """)
                fuel_data = [dict(r) for r in result]
            
            if fuel_data:
                for item in fuel_data:
                    if item["capacity"]:
                        st.markdown(f"**{item['fuel']}**: {item['capacity']:,} MW")
            else:
                st.info("No capacity data")
        
        with col2:
            st.markdown("**Capacity by Hub**")
            with kg.driver.session() as session:
                result = session.run("""
                    MATCH (p:Entity {type: 'PowerPlant'})-[:SUPPLIES]->(h)
                    RETURN h.name AS hub, sum(p.capacity_mw) AS capacity
                    ORDER BY capacity DESC
                """)
                hub_data = [dict(r) for r in result]
            
            if hub_data:
                for item in hub_data:
                    if item["capacity"]:
                        st.markdown(f"**{item['hub']}**: {item['capacity']:,} MW")
            else:
                st.info("No capacity data")
        
        # Renewable vs Non-renewable
        st.subheader("Renewable Energy Mix")
        with kg.driver.session() as session:
            result = session.run("""
                MATCH (p:Entity {type: 'PowerPlant'})-[:USES_FUEL]->(f)
                WITH sum(p.capacity_mw) AS total,
                     sum(CASE WHEN f.renewable = true THEN p.capacity_mw ELSE 0 END) AS renewable
                RETURN renewable, total, total - renewable AS non_renewable
            """)
            mix = result.single()
            
        if mix and mix["total"]:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Capacity", f"{mix['total']:,} MW")
            col2.metric("Renewable", f"{mix['renewable'] or 0:,} MW")
            col3.metric("Non-Renewable", f"{mix['non_renewable'] or 0:,} MW")
        else:
            st.info("No capacity data available")
    
    # Tab 3: Custom Query
    with tab3:
        st.subheader("Run Custom Cypher Query")
        
        default_query = """MATCH (n)-[r]->(m) 
RETURN n.name AS source, type(r) AS relationship, m.name AS target
LIMIT 20"""
        
        query = st.text_area("Cypher Query", value=default_query, height=100)
        
        if st.button("Run Query"):
            try:
                with kg.driver.session() as session:
                    result = session.run(query)
                    data = [dict(record) for record in result]
                
                if data:
                    st.dataframe(data)
                else:
                    st.info("Query returned no results")
            except Exception as e:
                st.error(f"Query error: {e}")
    
    kg.close()


if __name__ == "__main__":
    main()
