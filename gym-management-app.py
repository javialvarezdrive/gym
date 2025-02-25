import streamlit as st
import pandas as pd
from supabase import create_client
import uuid
from datetime import datetime

# Configuración de la página
st.set_page_config(
	page_title="Sistema de Gestión - Gimnasio",
	page_icon="💪",
	layout="wide"
)

# Credenciales de Supabase (Usando variables de entorno)
import os
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://jobetajndnzbzbljedio.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpvYmV0YWpuZG56YnpibGplZGlvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA1MDMwMjgsImV4cCI6MjA1NjA3OTAyOH0.tR-HR6s1WPYLVZrdV0f5oly1YFB3CQhFrCGyUIZt9Kw")

# Conexión a Supabase
def init_connection():
	try:
    	client = create_client(SUPABASE_URL, SUPABASE_KEY)
    	return client
	except Exception as e:
    	st.error(f"Error al conectar con Supabase: {e}")
    	return None

# Inicializar conexión
supabase = init_connection()

# Función para inicializar la base de datos (ejecutar una vez)
def init_database():
	# Crear tabla de usuarios si no existe
	supabase.table("usuarios_gimnasio").select("*").limit(1).execute()
    
	# Nota: La tabla se creará automáticamente en el panel de Supabase con las siguientes columnas:
	# id (UUID), nombre, apellidos, nip, seccion, grupo_trabajo, fecha_registro

# Función para agregar un usuario
def agregar_usuario(nombre, apellidos, nip, seccion, grupo_trabajo):
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

# Función para obtener todos los usuarios
def obtener_usuarios():
	try:
    	response = supabase.table("usuarios_gimnasio").select("*").order("apellidos").execute()
    	return pd.DataFrame(response.data)
	except Exception as e:
    	st.error(f"Error al obtener usuarios: {e}")
    	return pd.DataFrame()

# Función para buscar usuarios
def buscar_usuarios(termino_busqueda, campo="nip"):
	try:
    	if campo == "nip":
        	response = supabase.table("usuarios_gimnasio").select("*").eq(campo, termino_busqueda).execute()
    	else:
        	response = supabase.table("usuarios_gimnasio").select("*").ilike(campo, f"%{termino_busqueda}%").execute()
    	return pd.DataFrame(response.data)
	except Exception as e:
    	st.error(f"Error en la búsqueda: {e}")
    	return pd.DataFrame()

# Función para actualizar un usuario
def actualizar_usuario(id_usuario, nombre, apellidos, nip, seccion, grupo_trabajo):
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

# Función para eliminar un usuario
def eliminar_usuario(id_usuario):
	try:
    	response = supabase.table("usuarios_gimnasio").delete().eq("id", id_usuario).execute()
    	return True, "Usuario eliminado correctamente"
	except Exception as e:
    	return False, f"Error al eliminar usuario: {e}"

# Interfaz de usuario con Streamlit
def main():
	st.title("Sistema de Gestión - Gimnasio")
    
	# Menú lateral
	menu = st.sidebar.selectbox(
    	"Menú",
    	["Inicio", "Registrar Usuario", "Buscar Usuarios", "Gestionar Usuarios"]
	)
    
	# Página de inicio
	if menu == "Inicio":
    	st.header("Bienvenido al Sistema de Gestión de Gimnasio")
    	st.write("Seleccione una opción del menú para comenzar.")
   	 
    	# Estadísticas rápidas
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
    
	# Página para registrar usuarios
	elif menu == "Registrar Usuario":
    	st.header("Registrar Nuevo Usuario")
   	 
    	with st.form("registro_form"):
        	col1, col2 = st.columns(2)
       	 
        	with col1:
            	nombre = st.text_input("Nombre", "")
            	nip = st.text_input("NIP (Número único)", "")
            	grupo_trabajo = st.selectbox("Grupo de Trabajo", ["Grupo " + str(i) for i in range(1, 10)])
       	 
        	with col2:
            	apellidos = st.text_input("Apellidos", "")
            	seccion = st.selectbox("Sección", ["Motorista", "Patrullas", "GOA"])
       	 
        	submit_button = st.form_submit_button("Registrar Usuario")
       	 
        	if submit_button:
            	if nombre and apellidos and nip and seccion and grupo_trabajo:
                	# Verificar que el NIP no esté duplicado
                	df_check = buscar_usuarios(nip)
                	if not df_check.empty:
                    	st.error(f"Error: Ya existe un usuario con el NIP {nip}")
                	else:
                    	success, message = agregar_usuario(nombre, apellidos, nip, seccion, grupo_trabajo)
                    	if success:
                        	st.success(message)
                    	else:
                        	st.error(message)
            	else:
                	st.warning("Por favor complete todos los campos")
    
	# Página para buscar usuarios
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
    
	# Página para gestionar usuarios (editar/eliminar)
	elif menu == "Gestionar Usuarios":
    	st.header("Gestionar Usuarios")
   	 
    	# Obtener todos los usuarios
    	df = obtener_usuarios()
   	 
    	if not df.empty:
        	st.dataframe(df)
       	 
        	# Formulario para editar o eliminar
        	st.subheader("Editar o Eliminar Usuario")
       	 
        	# Seleccionar usuario por ID
        	user_ids = df["id"].tolist()
        	user_display = [f"{row['nip']} - {row['nombre']} {row['apellidos']}" for _, row in df.iterrows()]
       	 
        	selected_user_index = st.selectbox("Seleccionar Usuario", range(len(user_ids)), format_func=lambda x: user_display[x])
        	selected_user_id = user_ids[selected_user_index]
       	 
        	# Obtener datos del usuario seleccionado
        	selected_user = df[df["id"] == selected_user_id].iloc[0]
       	 
        	# Formulario para editar
        	with st.form("editar_form"):
            	col1, col2 = st.columns(2)
           	 
            	with col1:
                	nombre_edit = st.text_input("Nombre", selected_user["nombre"])
                	nip_edit = st.text_input("NIP", selected_user["nip"])
                	grupo_trabajo_edit = st.selectbox("Grupo de Trabajo",
                                                	["Grupo " + str(i) for i in range(1, 10)],
                                                	index=int(selected_user["grupo_trabajo"].split()[-1])-1 if "Grupo" in selected_user["grupo_trabajo"] else 0)
           	 
            	with col2:
                	apellidos_edit = st.text_input("Apellidos", selected_user["apellidos"])
                	seccion_edit = st.selectbox("Sección",
                                           	["Motorista", "Patrullas", "GOA"],
                                           	index=["Motorista", "Patrullas", "GOA"].index(selected_user["seccion"]) if selected_user["seccion"] in ["Motorista", "Patrullas", "GOA"] else 0)
           	 
            	col1, col2 = st.columns(2)
           	 
            	with col1:
                	update_button = st.form_submit_button("Actualizar Usuario")
           	 
            	with col2:
                	delete_button = st.form_submit_button("Eliminar Usuario", type="primary", help="Esta acción no se puede deshacer")
           	 
            	if update_button:
                	if nombre_edit and apellidos_edit and nip_edit and seccion_edit and grupo_trabajo_edit:
                    	# Verificar NIP duplicado (solo si cambió)
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
                	else:
                    	st.warning("Por favor complete todos los campos")
           	 
            	if delete_button:
                	# Confirmar eliminación
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


