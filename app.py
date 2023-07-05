from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


app = Flask(__name__)
app.config.from_pyfile('config.py')
from models import db
from models import Preceptor, Curso, Asistencia, Estudiante


@app.route('/')
def inicio():
    return render_template('inicio.html')


def validar_preceptor(clave, correo):
    completo = False
    usuario_actual = None
    usuario_actual = Preceptor.query.filter_by(correo=str(correo)).first()
    dbClave = usuario_actual.clave
    completo = check_password_hash(clave, dbClave)
    if completo is not True:
        usuario_actual = None
    return usuario_actual


@app.route('/Iniciar_sesion', methods=['GET', 'POST'])
def inicio_sesion():
    error = None
    if request.method == 'POST':
        correo = request.form['correo']
        clave = generate_password_hash(request.form['clave'])
        usuario_valido = validar_preceptor(clave, correo)
        if usuario_valido is None:
            error = 'Correo o clave inválida'
        else:
            session['usuario_id'] = usuario_valido.id
            return render_template('funciones_preceptor.html', usuario=usuario_valido)
    return render_template('inicio_sesion.html', error=error)


@app.route('/registrar_asistencia/<int:usuario_id>', methods=['GET', 'POST'])
def registrar_asistencia(usuario_id):
    if request.method == 'POST':
        curso_id = request.form['curso_id']
        fecha = request.form['fecha']
        clase = request.form['clase']
        estudiantes = Estudiante.query.filter_by(idcurso=int(curso_id)).order_by(Estudiante.apellido,
                                                                                 Estudiante.nombre).all()
        return render_template('cargar_asistencia.html', estudiantes=estudiantes, fecha=fecha, clase=clase,
                               curso_id=curso_id, usuario_id=usuario_id)

    cursos = Curso.query.filter_by(idpreceptor=usuario_id).all()
    return render_template('registrar_asistencia.html', cursos=cursos, usuario_id=usuario_id)


@app.route('/guardar_asistencia/<fecha>/<int:curso_id>/<int:clase>/<int:usuario_id>', methods=['POST', 'GET'])
def guardar_asistencia(fecha, curso_id, clase, usuario_id):
    fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
    estudiantes = Estudiante.query.filter_by(idcurso=int(curso_id)).order_by(Estudiante.nombre).all()
    for estudiante in estudiantes:
        asistencia_key = f'asistencia-{estudiante.id}'
        justificacion_key = f'justificacion-{estudiante.id}'
        asistencia = request.form.get(asistencia_key)
        justificacion = request.form.get(justificacion_key)
        if justificacion is None:
            justificacion = ""
        asistencia_nueva = Asistencia(fecha=fecha, codigoclase=int(clase), asistio=asistencia, justificacion=justificacion, idestudiante=estudiante.id)
        db.session.add(asistencia_nueva)
    db.session.commit()
    return render_template("guardar_asistencia.html", usuario_id=usuario_id)

@app.route('/informe_detallado/<int:usuario_id>/', methods=['GET', 'POST'])
def informe_detallado(usuario_id):
    cursos = Curso.query.filter_by(idpreceptor=usuario_id).all()
    informe = []

    if request.method == 'POST':
        curso_id = request.form.get('anio')
        estudiantes = Estudiante.query.filter_by(idcurso=int(curso_id)).order_by(Estudiante.apellido, Estudiante.nombre).all()

        for estudiante in estudiantes:
            asistencias = Asistencia.query.filter_by(idestudiante=estudiante.id).all()
            aula_asistencia = sum(1 for asistencia in asistencias if asistencia.asistio == 's' and asistencia.codigoclase == 1)
            asistencia_edu_fisica = sum(1 for asistencia in asistencias if asistencia.asistio == 's' and asistencia.codigoclase == 2)
            ausencia_justificada_aula = sum(1 for asistencia in asistencias if asistencia.asistio == 'n' and asistencia.codigoclase == 1 and asistencia.justificacion)
            ausencia_justificada_edu_fisica = sum(1 for asistencia in asistencias if asistencia.asistio == 'n' and asistencia.codigoclase == 2 and asistencia.justificacion)
            ausencia_injustificada_aula = sum(1 for asistencia in asistencias if asistencia.asistio == 'n' and asistencia.codigoclase == 1 and not asistencia.justificacion)
            ausencia_injustificada_edu_fisica = sum(1 for asistencia in asistencias if asistencia.asistio == 'n' and asistencia.codigoclase == 2 and not asistencia.justificacion)
            total_inasistencias = ausencia_injustificada_aula + (ausencia_injustificada_edu_fisica * 0.5)

            informe.append({
                'estudiante': estudiante,
                'aula_asistencia': aula_asistencia,
                'asistencia_edu_fisica': asistencia_edu_fisica,
                'ausencia_justificadas_aula': ausencia_justificada_aula,
                'ausencia_injustificadas_aula': ausencia_injustificada_aula,
                'ausencia_justificada_edu_fisica': ausencia_justificada_edu_fisica,
                'ausencia_injustificada_edu_fisica': ausencia_injustificada_edu_fisica,
                'total_inasistencias': total_inasistencias
            })

        return render_template('informe.html', estudiantes=estudiantes, informe=informe)

    return render_template('informe_detallado.html', cursos=cursos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)






'''

@app.route('/informe_detallado/<int:usuario_id>', methods=['GET', 'POST'])
def informe_detallado(usuario_id):
    informe = []
    cursos = Curso.query.filter_by(idpreceptor=usuario_id).all()

    if request.method == 'POST':
        curso_id = request.form['anio']
        estudiantes = Estudiante.query.filter_by(idcurso=int(curso_id)).order_by(Estudiante.apellido, Estudiante.nombre).all()

        for estudiante in estudiantes:
            asistencias = Asistencia.query.filter_by(idestudiante=int(estudiante.id)).all()
            aula_asistencia = sum(1 for asistencia in asistencias if asistencia.asistio == 's' and asistencia.codigoclase == 1)
            asistencia_edu_fisica = sum(1 for asistencia in asistencias if asistencia.asistio == 's' and asistencia.codigoclase == 2)
            ausencia_justificada_edu_fisica = sum(1 for asistencia in asistencias if asistencia.asistio == 'n' and asistencia.codigoclase == 2 and asistencia.justificacion != '')
            ausencia_justificada_aula = sum(1 for asistencia in asistencias if asistencia.asistio == 'n' and asistencia.codigoclase == 1 and asistencia.justificacion != '')
            ausencia_injustificada_aula = sum(1 for asistencia in asistencias if asistencia.asistio == 'n' and asistencia.codigoclase == 1 and asistencia.justificacion is not None)
            ausencia_injustificada_edu_fisica = sum(1 for asistencia in asistencias if asistencia.asistio == 'n' and asistencia.codigoclase == 2 and asistencia.justificacion is not None)
            total_inasistencias = ausencia_injustificada_aula + (ausencia_injustificada_edu_fisica * 0.5)
            informe.append({
                'estudiante': estudiante,
                'aula_asistencia': aula_asistencia,
                'asistencia_edu_fisica': asistencia_edu_fisica,
                'ausencia_justificadas_aula': ausencia_justificada_aula,
                'ausencia_injustificadas_aula': ausencia_injustificada_aula,
                'ausencia_justificada_edu_fisica': ausencia_justificada_edu_fisica,
                'ausencia_injustificada_edu_fisica': ausencia_injustificada_edu_fisica,
                'total_inasistencias': total_inasistencias
            })

        return render_template('informe.html', estudiantes=estudiantes, informe=informe)

    return render_template('informe_detallado.html', cursos=cursos)

'''