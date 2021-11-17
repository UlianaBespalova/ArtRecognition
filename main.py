from server import app, db
from server.models import Picture

@app.shell_context_processor
def make_shell_content():
    return {'db':db, 'Picture':Picture}
