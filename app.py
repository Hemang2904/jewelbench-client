import streamlit as st
import compute_rhino3d.Util
import compute_rhino3d.Grasshopper as gh
import rhino3dm
import json
import os
import requests

# --- Configuration ---
# REPLACE THIS WITH YOUR WINDOWS IP
WINDOWS_IP = "192.168.1.109" 
PORT = "5000"

# Setup Compute
compute_rhino3d.Util.url = f"http://{WINDOWS_IP}:{PORT}/"
# Since your server didn't enforce the API key in the log, we might not need it, 
# but best to keep it if you added it to the start script later.
# compute_rhino3d.Util.apiKey = "JB_SECRET_KEY_2026" 

st.set_page_config(page_title="JewelBench Hybrid", layout="wide")
st.title("💎 JewelBench: Hybrid CAD Engine")

# Sidebar
st.sidebar.header("Connection Status")
if st.sidebar.button("Test Connection"):
    try:
        resp = requests.get(f"http://{WINDOWS_IP}:{PORT}/health")
        if resp.status_code == 200:
            st.sidebar.success("✅ Connected to Windows Rhino!")
        else:
            st.sidebar.warning(f"⚠️ Server Reachable but returned {resp.status_code}")
    except Exception as e:
        st.sidebar.error(f"❌ Connection Failed: {e}")

# Main Logic
st.markdown("### 1. Upload Mesh (STL/OBJ)")
uploaded_file = st.file_uploader("Upload Ring File", type=['stl', 'obj'])

if uploaded_file:
    # Save Temp
    temp_path = "temp_input.stl"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.markdown("### 2. Process on Windows")
    if st.button("🚀 Run QuadRemesh & Scoop"):
        with st.spinner("Sending to Windows Node..."):
            try:
                # 1. Read Mesh
                mesh = rhino3dm.File3dm.Read(temp_path).Objects[0].Geometry
                
                # 2. Serialize
                arg = gh.DataTree("RH_IN:Mesh")
                arg.Append([0], [json.dumps(mesh.Encode())])
                
                # 3. Call Grasshopper (You need this file on Windows!)
                # Path must be LOCAL to the Windows machine
                gh_path = r"C:\JewelBench\Definitions\ScoopRing.gh"
                
                res = gh.EvaluateDefinition(gh_path, [arg])
                
                # 4. Decode Result
                # (Logic depends on GH output)
                st.success("Processing Complete! (Mock)")
                st.json(res)
                
            except Exception as e:
                st.error(f"Error: {e}")
