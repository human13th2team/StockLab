from flask import render_template
from . import analysis_bp

@analysis_bp.route('/report')
def report():
    return render_template('analysis/report.html')
