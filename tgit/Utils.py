import subprocess

def call( cmd, cwd=None, input=None ):
    if isinstance( input, str ):
        input = input.encode('utf-8')
    process = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE if input else None, cwd=cwd )
    stdoutput, stderroutput = process.communicate( input )
    try:
        return stdoutput.decode('utf-8').splitlines()
    except UnicodeDecodeError:
        return str( stdoutput ).split( '\\n' )

def call_nullSeperated( cmd, cwd=None, input=None ):
    if isinstance( input, str ):
        input = input.encode('utf-8')
    process = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE if input else None, cwd=cwd )
    stdoutput, stderroutput = process.communicate( input )
    outputList = stdoutput.split( b'\x00' )
    try:
        outputStrings = map( lambda s: s.decode('utf-8'), outputList )
    except UnicodeDecodeError:
        outputStrings = map( lambda s: str( s ), outputList )
    return list( outputStrings )
