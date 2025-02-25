import streamlit as st
import pandas as pd
from supabase import create_client
import uuid
from datetime import datetime
import os

# --- Constants ---
SECTIONS = ["Motorista", "Patrullas", "GOA"]
GRUPOS_TRABAJO = ["Grupo " + str(i) for i in range(1, 10)]

# --- Supabase Credentials from Environment Variables (No Defaults!) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# --- Page Configuration ---
st.set_page_config(
    page_title="Sistema de Gestión - Gimnasio",
    page_icon="💪",
    layout="wide"
)

# --- Database Connection ---
def init_connection():
    """Initializes and returns a Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Error: Supabase URL and Key environment variables are not set.")
        return None
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        return None

# Initialize connection
supabase = init_connection()

# --- Database Initialization (Run once) ---
def init_database():
    """Initializes the database (creates tables if needed - not fully implemented here)."""
    # Basic check if table exists (more robust checks might be needed in real app)
    if supabase:
        try:
            supabase.table("usuarios_gimnasio").select("*").limit(1).execute()
            # Table assumed to exist if no error. In real app, check for specific error if table doesn't exist and create it.
        except Exception:
            st.warning("Tabla 'usuarios_gimnasio' no encontrada o error al verificar. Asegúrese de que la tabla existe en Supabase.")

# --- User Management Functions ---
def agregar_usuario(nombre, apellidos, nip, seccion, grupo_trabajo):
    """Adds a new user to the database."""
    if not supabase: return False, "Conexión a Supabase no inicializada."
    try:
        data = {
            "id": str(uuid.uuid4()),
            "nombre": nombre,
            "apellidos": apellidos,
            "nip": nip,
            "seccion": seccion,
            "grupo_trabajo": grupo_trabajo,
            "fecha_registro": datetime.now().isoformat()
        }
        response = supabase.table("usuarios_gimnasio").insert(data).execute()
        return True, "Usuario registrado con éxito"
    except Exception as e:
        return False, f"Error al registrar usuario: {e}"

def obtener_usuarios():
    """Retrieves all users from the database."""
    if not supabase: return pd.DataFrame()
    try:
        response = supabase.table("usuarios_gimnasio").select("*").order("apellidos").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error al obtener usuarios: {e}")
        return pd.DataFrame()

def buscar_usuarios(termino_busqueda, campo="nip"):
    """Searches for users based on a search term and field."""
    if not supabase: return pd.DataFrame()
    try:
        if campo == "nip":
            response = supabase.table("usuarios_gimnasio").select("*").eq(campo, termino_busqueda).execute()
        else:
            response = supabase.table("usuarios_gimnasio").select("*").ilike(campo, f"%{termino_busqueda}%").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error en la búsqueda: {e}")
        return pd.DataFrame()

def actualizar_usuario(id_usuario, nombre, apellidos, nip, seccion, grupo_trabajo):
    """Updates an existing user's information."""
    if not supabase: return False, "Conexión a Supabase no inicializada."
    try:
        data = {
            "nombre": nombre,
            "apellidos": apellidos,
            "nip": nip,
            "seccion": seccion,
            "grupo_trabajo": grupo_trabajo,
            "actualizado_el": datetime.now().isoformat()
        }
        response = supabase.table("usuarios_gimnasio").update(data).eq("id", id_usuario).execute()
        return True, "Usuario actualizado correctamente"
    except Exception as e:
        return False, f"Error al actualizar usuario: {e}"

def eliminar_usuario(id_usuario):
    """Deletes a user from the database."""
    if not supabase: return False, "Conexión a Supabase no inicializada."
    try:
        response = supabase.table("usuarios_gimnasio").delete().eq("id", id_usuario).execute()
        return True, "Usuario eliminado correctamente"
    except Exception as e:
        return False, f"Error al eliminar usuario: {e}"

# --- Streamlit UI ---
def main():
    init_database() # Initialize database check on app start
    st.title("Sistema de Gestión - Gimnasio")

    # --- Sidebar Menu ---
    menu = st.sidebar.selectbox(
        "Menú",
        ["Inicio", "Registrar Usuario", "Buscar Usuarios", "Gestionar Usuarios"]
    )

    # --- Inicio Page ---
    if menu == "Inicio":
        st.header("Bienvenido al Sistema de Gestión de Gimnasio")
        st.write("Seleccione una opción del menú para comenzar.")

        # --- Quick Statistics ---
        st.subheader("Estadísticas")

        try:
            df = obtener_usuarios()
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Usuarios", len(df))

            with col2:
                if not df.empty and 'seccion' in df.columns:
                    seccion_counts = df['seccion'].value_counts()
                    st.write("Usuarios por Sección")
                    st.dataframe(seccion_counts)

            with col3:
                if not df.empty and 'grupo_trabajo' in df.columns:
                    grupo_counts = df['grupo_trabajo'].value_counts()
                    st.write("Usuarios por Grupo")
                    st.dataframe(grupo_counts)
        except:
            st.warning("No se pudieron cargar las estadísticas")

    # --- Registrar Usuario Page ---
    elif menu == "Registrar Usuario":
        st.header("Registrar Nuevo Usuario")

        with st.form("registro_form"):
            col1, col2 = st.columns(2)

            with col1:
                nombre = st.text_input("Nombre", "")
                nip = st.text_input("NIP (Número único)", "")
                grupo_trabajo = st.selectbox("Grupo de Trabajo", GRUPOS_TRABAJO)

            with col2:
                apellidos = st.text_input("Apellidos", "")
                seccion = st.selectbox("Sección", SECTIONS)

            submit_button = st.form_submit_button("Registrar Usuario")

            if submit_button:
                if not nombre or not apellidos or not nip or not seccion or not grupo_trabajo:
                    st.warning("Por favor complete todos los campos")
                elif not nip.isdigit() or len(nip) != 6:  # NIP validation: 6 digits numeric
                    st.warning("NIP debe ser numérico y tener 6 dígitos.")
                else:
                    df_check = buscar_usuarios(nip)
                    if not df_check.empty:
                        st.error(f"Error: Ya existe un usuario con el NIP {nip}")
                    else:
                        success, message = agregar_usuario(nombre, apellidos, nip, seccion, grupo_trabajo)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

    # --- Buscar Usuarios Page ---
    elif menu == "Buscar Usuarios":
        st.header("Buscar Usuarios")

        col1, col2 = st.columns([3, 1])

        with col1:
            search_term = st.text_input("Término de búsqueda", "")

        with col2:
            search_field = st.selectbox("Buscar por", ["nip", "nombre", "apellidos", "seccion", "grupo_trabajo"])

        if st.button("Buscar"):
            if search_term:
                results = buscar_usuarios(search_term, search_field)
                if not results.empty:
                    st.dataframe(results)
                    st.success(f"Se encontraron {len(results)} resultados")
                else:
                    st.info("No se encontraron resultados")
            else:
                st.warning("Ingrese un término de búsqueda")

    # --- Gestionar Usuarios Page ---
    elif menu == "Gestionar Usuarios":
        st.header("Gestionar Usuarios")

        df = obtener_usuarios()

        if not df.empty:
            st.dataframe(df)

            # --- Edit/Delete User Form ---
            st.subheader("Editar o Eliminar Usuario")

            user_ids = df["id"].tolist()
            user_display = [f"{row['nip']} - {row['nombre']} {row['apellidos']}" for _, row in df.iterrows()]

            selected_user_index = st.selectbox("Seleccionar Usuario", range(len(user_ids)), format_func=lambda x: user_display[x])
            selected_user_id = user_ids[selected_user_index]

            selected_user = df[df["id"] == selected_user_id].iloc[0]

            with st.form("editar_form"):
                col1, col2 = st.columns(2)

                with col1:
                    nombre_edit = st.text_input("Nombre", selected_user["nombre"])
                    nip_edit = st.text_input("NIP", selected_user["nip"])
                    grupo_trabajo_edit = st.selectbox("Grupo de Trabajo",
                                                    GRUPOS_TRABAJO,
                                                    index=GRUPOS_TRABAJO.index(selected_user["grupo_trabajo"]) if selected_user["grupo_trabajo"] in GRUPOS_TRABAJO else 0) # corrected index

                with col2:
                    apellidos_edit = st.text_input("Apellidos", selected_user["apellidos"])
                    seccion_edit = st.selectbox("Sección",
                                               SECTIONS,
                                               index=SECTIONS.index(selected_user["seccion"]) if selected_user["seccion"] in SECTIONS else 0) # corrected index


                col1, col2 = st.columns(2)

                with col1:
                    update_button = st.form_submit_button("Actualizar Usuario")

                with col2:
                    delete_button = st.form_submit_button("Eliminar Usuario", type="primary", help="Esta acción no se puede deshacer")

                if update_button:
                    if not nombre_edit or not apellidos_edit or not nip_edit or not seccion_edit or not grupo_trabajo_edit:
                        st.warning("Por favor complete todos los campos")
                    elif not nip_edit.isdigit() or len(nip_edit) != 6: # NIP validation: 6 digits numeric - on edit as well
                        st.warning("NIP debe ser numérico y tener 6 dígitos.")
                    else:
                        if nip_edit != selected_user["nip"]:
                            df_check = buscar_usuarios(nip_edit)
                            if not df_check.empty:
                                st.error(f"Error: Ya existe un usuario con el NIP {nip_edit}")
                                st.stop()

                        success, message = actualizar_usuario(
                            selected_user_id, nombre_edit, apellidos_edit,
                            nip_edit, seccion_edit, grupo_trabajo_edit
                        )

                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)

                if delete_button:
                    if st.session_state.get('confirm_delete') != selected_user_id:
                        st.session_state['confirm_delete'] = selected_user_id
                        st.warning(f"¿Está seguro de eliminar a {selected_user['nombre']} {selected_user['apellidos']}? Presione nuevamente para confirmar.")
                    else:
                        success, message = eliminar_usuario(selected_user_id)
                        if success:
                            st.session_state.pop('confirm_delete')
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
        else:
            st.info("No hay usuarios registrados aún")

if __name__ == "__main__":
    main()
