# Standard library imports
import json
import logging
from uuid import uuid4
from flask_cors import CORS
from threading import Thread
from datetime import datetime
from dotenv import load_dotenv
from crew import CompanyResearchCrew
from flask import Flask, jsonify, request, abort
from job_manager import append_event, jobs, jobs_lock, Event


load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def kickoff_crew(job_id, companies: list[str], positions: list[str]):
    logging.info(f"Crew for job {job_id} is starting")

    results = None
    try:
        company_research_crew = CompanyResearchCrew(job_id)
        company_research_crew.setup_crew(
            companies, positions)
        results = company_research_crew.kickoff()
        logging.info(f"Crew for job {job_id} is complete", results)

    except Exception as e:
        logging.error(f"Error in kickoff_crew for job {job_id}: {e}")
        append_event(job_id, f"An error occurred: {e}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)

    with jobs_lock:
        jobs[job_id].status = 'COMPLETE'
        jobs[job_id].result = results
        jobs[job_id].events.append(
            Event(timestamp=datetime.now(), data="Crew complete"))


@app.route('/api/crew', methods=['POST'])
def run_crew():
    logging.info("Received request to run crew")
    # Validation
    data = request.json
    if not data or 'companies' not in data or 'positions' not in data:
        abort(400, description="Invalid input data provided.")

    job_id = str(uuid4())
    companies = data['companies']
    positions = data['positions']

    thread = Thread(target=kickoff_crew, args=(
        job_id, companies, positions))
    thread.start()

    return jsonify({"job_id": job_id}), 202


@app.route('/api/crew/<job_id>', methods=['GET'])
@app.route('/api/crew/<job_id>', methods=['GET'])
def get_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            abort(404, description="Job not found")

    # Parse the job.result string into a JSON object if job.result is not None
    if job.result is not None:
        try:
            result_json = json.loads(job.result)
        except json.JSONDecodeError:
            # If parsing fails, set result_json to the original job.result string
            result_json = job.result
    else:
        result_json = None

    return jsonify({
        "job_id": job_id,
        "status": job.status,
        "result": result_json,
        "events": [{"timestamp": event.timestamp.isoformat(), "data": event.data} for event in job.events]
    })


if __name__ == '__main__':
    app.run(debug=True, port=3001)