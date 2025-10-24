import streamlit as st
import epyt
import matplotlib.pyplot as plt
import io
import base64

# Upload network file
uploaded_file = st.file_uploader("Upload EPANET .inp file", type=['inp'])

if uploaded_file:
    # Load network
    network = epyt.epanet(uploaded_file)
    
    # Use EPANET's native plot method directly!
    fig, ax = plt.subplots(figsize=(12, 8))
    network.plot(ax=ax, title="Network Visualization")
    
    # Display the plot
    st.pyplot(fig)
    
    # Show network info
    st.write("Network Summary:")
    st.write(f"Nodes: {network.getNodeCount()}")
    st.write(f"Links: {network.getLinkCount()}")