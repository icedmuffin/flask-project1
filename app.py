from flask import Flask, render_template, request
from expertSystem import inference
from helperFunction import reshape
import joblib
import pandas as pd

app = Flask(__name__)


# post csv ke database
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("index.html")


@app.route("/heart_disease_prediction", methods=["POST", "GET"])
# @cross_origin()
def heart_disease():
    if request.method == "POST":

        # get input
        age = int(request.form['age'])
        sex = int(request.form['sex'])
        chest_paint_type = int(request.form['chestPainType'])
        resting_bps = int(request.form['restingBloodPressure'])
        fasting_blood_sugar = int(request.form['fastingBloodSugar'])
        max_heart_rate = int(request.form['maxHeartRate'])
        exercise_angina = int(request.form['exerciseAngina'])
        old_peak = float(request.form['oldpeak'])
        st_slope = int(request.form['stSlope'])

        # prepare input
        pred_input = [age,
                      sex,
                      chest_paint_type,
                      resting_bps,
                      fasting_blood_sugar,
                      max_heart_rate,
                      exercise_angina,
                      old_peak,
                      st_slope]

        # append input here
        # age, sex, chest pain type, fasting blood sugar, max heart rate, exercise angina, old-peak, ST slope
        pred_prob = load_model.predict([pred_input])
        predict = (pred_prob >= 0.43).astype(int).reshape(-1)

        # --getting probability number
        probability_number = pred_prob[0][0]

        # --assign level based on probability number
        if 0 <= probability_number <= 0.43:
            probability_level = 1  # normal
        elif 0.44 <= probability_number <= 0.80:
            probability_level = 2  # gray area
        elif 0.81 <= probability_number <= 1.0:
            probability_level = 3  # high chance
        else:
            return "probability number '" + probability_number + "' should have been a number or between 0-100 please " \
                                                                 "check again"

        return render_template("/prediction-result.html",
                               probability_level=probability_level,
                               probability_number=probability_number,
                               sex=sex)
    else:
        return render_template("/heart-disease-prediction.html")


@app.route('/expert_system', methods=['POST', 'GET'])
def expert_system():
    if request.method == 'POST':

        # --getting value
        evidences = request.form.getlist('selected_evident') + request.form.getlist('selected_history')
        intolerance = request.form.getlist('selected_intolerance')
        sex = request.form.get('selected_sex')
        measurements = []

        measurement_input = ['lvef', 'gfr', 'potassium', 
                             'resting_heart_rate', 'qrs']

        for measurement in measurement_input:
            input_value = request.form.get(measurement)
            if input_value:
                measurements.append({measurement: int(input_value)})

        # initiate prolog
        result = inference(evidences, measurements, intolerance, sex)

        return render_template('/expert-system-result.html',
                               recommendation_result=result)

    else:
        return render_template('/expert-system.html',
                               eveident_selection_value=evidence_value,
                               eveident_selection_desc=evidence_desc,
                               total_eveident_selection=len(evidence_value),

                               history_selection_value=history_value,
                               history_selection_desc=history_desc,
                               total_history_selection=len(history_value),

                               intolearant_selection_value=intolerant_value,
                               intolearant_selection_desc=intolerant_desc,
                               total_intolearant_selection=len(intolerant_value),

                               measurement_value=measurements_input,
                               measurement_desc=measurements_desc,
                               measurement_unit=measurements_unit,
                               total_measurement=len(measurements_input)
                               )


# bridge from expert system result result
@app.route('/bridge', methods=['POST'])
def bridge():
    if request.method == 'POST':
        try:
            ps_patient_sex = request.form.get('ps_patient_sex')
            ps_patient_diagnoses = request.form.get('ps_patient_diagnose_result')

            if ps_patient_sex == '1':
                ps_patient_sex = 'male'
            elif ps_patient_sex == '0':
                ps_patient_sex = 'female'
            else:
                return "ps_patient_sex value does not fit the requirement should be string" \
                       " '0' or '1'"
        #     fix sex from number into string

        except():
            return "patient sex and patient diagnose value didn't pass"

        return render_template('/expert-system.html',
                               eveident_selection_value=evidence_value,
                               eveident_selection_desc=evidence_desc,
                               total_eveident_selection=len(evidence_value),

                               history_selection_value=history_value,
                               history_selection_desc=history_desc,
                               total_history_selection=len(history_value),

                               intolearant_selection_value=intolerant_value,
                               intolearant_selection_desc=intolerant_desc,
                               total_intolearant_selection=len(intolerant_value),

                               measurement_value=measurements_input,
                               measurement_desc=measurements_desc,
                               measurement_unit=measurements_unit,
                               total_measurement=len(measurements_input),

                               ps_patient_sex=ps_patient_sex,
                               ps_patient_diagnoses=ps_patient_diagnoses
                               )
    else:
        return "wrong use of route, meant to be from prediction result into expert system form"


if __name__ == "__main__":
    # load the model from disk
    filename = 'model.pkl'
    load_model = joblib.load(filename)

    # load data input for expert system input
    input_df = pd.read_csv('csv/input.csv')
    evidence_value = input_df[input_df['type'] == 'evidence']['input'].tolist()
    evidence_desc = input_df[input_df['type'] == 'evidence']['desc'].tolist()

    history_value = input_df[input_df['type'] == 'History']['input'].tolist()
    history_desc = input_df[input_df['type'] == 'History']['desc'].tolist()

    intolerant_value = input_df[input_df['type'] == 'intolerant']['input'].tolist()
    intolerant_desc = input_df[input_df['type'] == 'intolerant']['desc'].tolist()

    measurement_df = pd.read_csv('csv/measurement.csv')
    measurements_input = measurement_df['measurement']
    measurements_desc = measurement_df['desc']
    measurements_unit = measurement_df['unit']

    app.run(debug=True)
