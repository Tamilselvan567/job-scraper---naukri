import os
import pandas as pd
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from scraper import scrape_naukri_jobs

app = Flask(__name__)
# Secret key needed for flash messages
app.secret_key = "secret_key_for_job_scraper"

# Global variable to hold scraped dataframe temporarily (in-memory)
# In a production app, this should be stored in a database or tied to a user session
scraped_data_df = pd.DataFrame()

@app.route("/", methods=["GET", "POST"])
def index():
    global scraped_data_df
    jobs = []
    
    if request.method == "POST":
        role = request.form.get("role")
        location = request.form.get("location")
        max_jobs = request.form.get("max_jobs", 50) # Default to 50 for quick demo
        
        try:
            max_jobs = int(max_jobs)
        except ValueError:
            max_jobs = 50
            
        if not role or not location:
            flash("Please enter both Job Role and Location.", "error")
            return render_template("index.html", jobs=[])
            
        print(f"Starting scraping for Role: {role}, Location: {location}, Max Jobs: {max_jobs}")
        try:
            # Call the scraper function
            scraped_jobs = scrape_naukri_jobs(role, location, max_jobs=max_jobs)
            
            if scraped_jobs:
                # Convert the result to a Pandas DataFrame
                scraped_data_df = pd.DataFrame(scraped_jobs)
                jobs = scraped_jobs
                flash(f"Successfully scraped {len(jobs)} jobs!", "success")
            else:
                flash("No jobs found for the given criteria or could not scrape. Please try again.", "error")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            
    return render_template("index.html", jobs=jobs)

@app.route("/download")
def download_csv():
    global scraped_data_df
    
    # Check if we have data to download
    if scraped_data_df.empty:
        flash("No data available to download. Please scrape some jobs first.", "error")
        return redirect(url_for('index'))
        
    # Define a temporary path to save the CSV
    csv_filename = "jobs.csv"
    csv_filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), csv_filename)
    
    try:
        # Export DataFrame to CSV
        scraped_data_df.to_csv(csv_filepath, index=False)
        # Send the file to the user for download
        return send_file(csv_filepath, as_attachment=True, download_name="jobs.csv")
    except Exception as e:
        flash(f"Error generating CSV: {str(e)}", "error")
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
