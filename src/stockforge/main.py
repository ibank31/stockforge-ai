import typer
from stockforge import __version__
app=typer.Typer()
@app.command()
def version(): print(__version__)
if __name__=='__main__': app()
