import os
import io
import base64
import qrcode
from nicegui import ui, app
from database import engine
from models import SQLModel
from sqlmodel import Session
import crud
from exporters import generate_qr_svg, generate_qr_pdf

SQLModel.metadata.create_all(engine)

app.storage.user['user_id'] = None
app.storage.user['username'] = None

def get_qr_image_base64(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

@ui.page('/')
def index():
    if not app.storage.user.get('user_id'):
        return render_auth_view()
    return render_dashboard_view()

def render_auth_view():
    with ui.card().classes('w-96 mx-auto mt-20 p-6 shadow-lg rounded-lg'):
        ui.label('QR Cloud Manager').classes('text-2xl font-bold mb-4 text-center')
        
        tab = ui.tabs().classes('w-full')
        with tab:
            login_tab = ui.tab('Iniciar Sesión')
            register_tab = ui.tab('Registrarse')
            
        with ui.tab_panels(tab, value=login_tab).classes('w-full'):
            with ui.tab_panel(login_tab):
                username_in = ui.input('Usuario').classes('w-full')
                password_in = ui.input('Contraseña', password=True).classes('w-full')
                
                def handle_login():
                    with Session(engine) as session:
                        user = crud.authenticate_user(session, username_in.value, password_in.value)
                        if user:
                            app.storage.user['user_id'] = user.id
                            app.storage.user['username'] = user.username
                            ui.navigate.to('/')
                        else:
                            ui.notify('Credenciales inválidas', color='negative')
                
                ui.button('Entrar', on_click=handle_login).props('color=primary').classes('w-full mt-4')

            with ui.tab_panel(register_tab):
                reg_user = ui.input('Nuevo Usuario').classes('w-full')
                reg_pass = ui.input('Contraseña', password=True).classes('w-full')
                
                def handle_register():
                    with Session(engine) as session:
                        user = crud.register_user(session, reg_user.value, reg_pass.value)
                        if user:
                            ui.notify('Registro exitoso. Inicia sesión.', color='positive')
                        else:
                            ui.notify('El usuario ya existe', color='negative')
                
                ui.button('Registrarse', on_click=handle_register).props('color=secondary').classes('w-full mt-4')

def render_dashboard_view():
    username = app.storage.user.get('username')
    user_id = app.storage.user.get('user_id')

    with ui.row().classes('w-full justify-between items-center p-4 bg-gray-100 shadow'):
        ui.label(f'Bienvenido, {username}').classes('text-xl font-semibold')
        def logout():
            app.storage.user['user_id'] = None
            app.storage.user['username'] = None
            ui.navigate.to('/')
        ui.button('Cerrar Sesión', on_click=logout).props('flat color=negative')

    with ui.row().classes('w-full p-6 gap-6'):
        with ui.card().classes('w-1/2 p-6'):
            ui.label('Generar Nuevo Código QR').classes('text-xl font-bold mb-4')
            title_input = ui.input('Título o Descripción del QR').classes('w-full')
            content_input = ui.textarea('Texto o URL a codificar').classes('w-full')
            
            qr_display = ui.column().classes('mt-4 items-center w-full')

            def generate_qr():
                if not content_input.value or not title_input.value:
                    ui.notify('Completa todos los campos', color='warning')
                    return
                
                title = title_input.value
                content = content_input.value
                
                with Session(engine) as session:
                    crud.save_qr_history(session, user_id, title, content)
                
                qr_display.clear()
                with qr_display:
                    qr_base64 = get_qr_image_base64(content)
                    ui.image(qr_base64).classes('w-48 h-48')
                    ui.label('¡QR Generado y Guardado en el Historial!').classes('text-green-600 text-sm mt-2')
                    
                    with ui.row().classes('mt-4 gap-4'):
                        def download_svg():
                            svg_bytes = generate_qr_svg(content)
                            ui.download(svg_bytes, filename=f"{title}_qr.svg")
                            ui.notify('Descargando SVG...', color='info')
                        ui.button('Descargar SVG', on_click=download_svg, icon='download').props('outline color=primary')

                        def download_pdf():
                            pdf_bytes = generate_qr_pdf(content, title)
                            ui.download(pdf_bytes, filename=f"{title}_qr.pdf")
                            ui.notify('Exportando PDF...', color='info')
                        ui.button('Exportar PDF', on_click=download_pdf, icon='picture_as_pdf').props('color=secondary')

                refresh_history()

            ui.button('Crear y Guardar QR', on_click=generate_qr).props('color=primary').classes('mt-4')

        with ui.card().classes('w-1/2 p-6'):
            ui.label('Tu Historial en la Nube').classes('text-xl font-bold mb-4')
            history_container = ui.column().classes('w-full overflow-y-auto max-h-96')

            def refresh_history():
                history_container.clear()
                with history_container:
                    with Session(engine) as session:
                        items = crud.get_user_history(session, user_id)
                    
                    if not items:
                        ui.label('No tienes códigos generados aún.').classes('text-gray-400')
                    
                    for item in items:
                        with ui.card().classes('w-full p-3 mb-2 bg-gray-50'):
                            ui.label(item.title).classes('font-bold')
                            ui.label(f"Contenido: {item.content}").classes('text-xs text-gray-600 truncate')
                            ui.label(f"Creado: {item.created_at.strftime('%Y-%m-%d %H:%M')}").classes('text-xs text-gray-400')

            refresh_history()

port = int(os.environ.get("PORT", 8080))
ui.run(port=port, title='QR Cloud Hub', host='0.0.0.0', storage_secret='secret_key_nicegui_qr_cloud')
