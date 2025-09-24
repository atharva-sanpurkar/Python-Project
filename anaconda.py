from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)
df = None

#  "Inherited Will" - Just like data persists through routes, dreams pass on in One Piece.


@app.route('/')
def home():
    return render_template('hyper.html')


@app.route('/upload', methods=['POST'])
def upload():
    global df
    file = request.files['file']
    df = pd.read_csv(file)

    # Compute totals and ranks
    # Believe it! (Naruto) – every student’s true power shows in the sum.
    df['Total'] = df[['DM', 'MEFA', 'DT', 'Python']].sum(axis=1)
    df['Rank'] = df['Total'].rank(ascending=False, method="min").astype(int)

    return jsonify({
        "message": "File uploaded successfully!",
        "students": df[['Name', 'Total']].to_dict(orient="records")
    })


@app.route('/filter')
def filter_data():
    global df
    if df is None:
        return jsonify({"error": "No file uploaded"})

    subject = request.args.get("subject")
    section = request.args.get("section")
    low = request.args.get("low", type=int)
    high = request.args.get("high", type=int)
    mode = request.args.get("mode", "all")

    data = df.copy()

    if section:
        data = data[data['Section'].astype(str).str.upper() == section.upper()]

    if subject and subject not in df.columns:
        return jsonify({"error": f"Invalid subject {subject}"})

    if low is not None and high is not None:
        if subject:
            data = data[(data[subject] >= low) & (data[subject] <= high)]
        else:
            data = data[(data['Total'] >= low) & (data['Total'] <= high)]

    if data.empty:
        return jsonify({"error": "No data found for given filters"})

    # Like Levi choosing the best move: topper logic
    if mode == "topper":
        if subject:
            topper = data.loc[data[subject].idxmax()]
            return jsonify(topper.to_dict())
        else:
            topper = data.loc[data['Total'].idxmax()]
            return jsonify(topper.to_dict())
    else:
        if subject:
            return jsonify(data[['Name', subject]].to_dict(orient="records"))
        else:
            return jsonify(data[['Name', 'Total']].to_dict(orient="records"))


@app.route('/student/<roll_no>')
def student_graph(roll_no):
    global df
    if df is None:
        return jsonify({"error": "No file uploaded"})
    student = df[df['Roll No'].astype(str) == str(roll_no)]
    if student.empty:
        return jsonify({"error": "Student not found"})
    # Every shinobi (student) has their own story in the graph.
    return jsonify(student.to_dict(orient="records")[0])


# ---------- Export Route ----------
@app.route('/export')
def export_csv():
    global df
    if df is None:
        return jsonify({"error": "No file uploaded"})

    mode = request.args.get("mode", "all")
    subject = request.args.get("subject")
    section = request.args.get("section")
    roll_no = request.args.get("roll_no")

    data = df.copy()

    # --- Student Report ---
    # Just like Naruto carried Kurama, each student carries their marks.
    if mode == "student":
        if not roll_no:
            return jsonify({"error": "Roll number required for student export"})
        student = data[data['Roll No'].astype(str) == str(roll_no)]
        if student.empty:
            return jsonify({"error": "Student not found"})
        if subject and subject in df.columns:
            student = student[['Roll No', 'Name', 'Section', subject]]
        filename = f"student_{roll_no}{'_' + subject if subject else ''}.csv"
        return student.to_csv(index=False), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename="{filename}"'
        }

    # --- Section Report ---
    # "Together, comrades stand against walls." – AOT
    if mode == "section":
        if not section:
            return jsonify({"error": "Section required for section export"})
        sec_data = data[data['Section'].astype(
            str).str.upper() == section.upper()]
        if sec_data.empty:
            return jsonify({"error": f"No data found for Section {section}"})

        if subject and subject in df.columns:
            # Export only that subject for the section
            sec_data = sec_data[['Roll No', 'Name', 'Section', subject]].copy()
            sec_data['Rank_in_' + subject] = sec_data[subject].rank(
                ascending=False, method="min").astype(int)
            filename = f"section_{section}_{subject}.csv"
        else:
            # Export all subjects for the section
            sec_data = sec_data[['Roll No', 'Name', 'Section',
                                 'DM', 'MEFA', 'DT', 'Python', 'Total', 'Rank']]
            filename = f"section_{section}_all_subjects.csv"

        return sec_data.to_csv(index=False), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename="{filename}"'
        }

    # --- Subject Report ---
    # Zoro aims for the top, so does each subject topper.
    if mode == "subject":
        if not subject or subject not in df.columns:
            return jsonify({"error": "Valid subject required"})
        subj_data = data[['Roll No', 'Name', 'Section', subject]].copy()
        if section:
            subj_data = subj_data[subj_data['Section'].astype(
                str).str.upper() == section.upper()]
        subj_data['Rank_in_' + subject] = subj_data[subject].rank(
            ascending=False, method="min").astype(int)
        filename = f"subject_{subject}{'_' + section if section else ''}.csv"
        return subj_data.to_csv(index=False), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename="{filename}"'
        }

    # --- Overall Report ---
    if section:
        data = data[data['Section'].astype(str).str.upper() == section.upper()]
    if subject and subject in df.columns:
        data = data[['Roll No', 'Name', 'Section', subject]]
    filename = f"overall_report{'_' + section if section else ''}{'_' + subject if subject else ''}.csv"

    return data.to_csv(index=False), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename="{filename}"'
    }


if __name__ == '__main__':
    #  "Keep moving forward." – Eren Yeager
    app.run(debug=True)
