usuarios_seleccionados = st.multiselect(
                        "Seleccionar usuarios para esta actividad",
                        options=list(opciones_usuarios.keys()),
                        format_func=lambda x: opciones_usuarios[x]
                    )
                else:
                    st.warning("No hay usuarios disponibles para asignar")
                    usuarios_seleccionados = []
                
                crear_button = st.form_submit_button("Crear Actividad")
                
                if crear_button:
                    if titulo and fecha_actividad and hora_inicio and hora_fin:
                        # Validar hora de inicio < hora de fin
                        if hora_inicio >= hora_fin:
                            st.error("La hora de inicio debe ser anterior a la hora de fin")
                        else:
                            # Guardar actividad
                            fecha_str = fecha_actividad.isoformat()
                            hora_inicio_str = hora_inicio.strftime("%H:%M")
                            hora_fin_str = hora_fin.strftime("%H:%M")
                            
                            success, actividad_id, message = agregar_actividad(
                                titulo, descripcion, fecha_str, hora_inicio_str, hora_fin_str
                            )
                            
                            if success and actividad_id:
                                # Asignar usuarios
                                if usuarios_seleccionados:
                                    success2, message2 = asignar_usuarios_actividad(actividad_id, usuarios_seleccionados)
                                    if success2:
                                        st.success(f"{message} - {message2}")
                                        st.experimental_rerun()
                                    else:
                                        st.error(message2)
                                else:
                                    st.success(f"{message} (Sin usuarios asignados)")
                                    st.experimental_rerun()
                            else:
                                st.error(message)
                    else:
                        st.warning("Debe completar al menos el título, fecha y horarios")

if __name__ == "__main__":
    main()
