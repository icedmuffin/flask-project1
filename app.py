from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import expertSystem
import heart_prediction_default_input

from flask import Flask, render_template, request
# from flask_cors import CORS, cross_origin
import joblib
import numpy as np

app = Flask(__name__)


# post csv ke database
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("index.html")


# input csv
heart_diseases_input = heart_prediction_default_input.value


@app.route("/heart_disease_prediction", methods=["POST", "GET"])
# @cross_origin()
def heart_disease():
    if request.method == "POST":

        # get input
        # age = int(request.form['age'])
        # sex = int(request.form['sex'])
        # chest_paint_type = int(request.form['chestPainType'])
        # resting_bps = int(request.form['restingBloodPressure'])
        # fasting_blood_sugar = int(request.form['fastingBloodSugar'])
        # max_heart_rate = int(request.form['maxHeartRate'])
        # exercise_angina = int(request.form['exerciseAngina'])
        # old_peak = float(request.form['oldpeak'])
        # st_slope = int(request.form['stSlope'])
        #
        # # prepare input
        # pred_input = [age,
        #               sex,
        #               chest_paint_type,
        #               resting_bps,
        #               fasting_blood_sugar,
        #               max_heart_rate,
        #               exercise_angina,
        #               old_peak,
        #               st_slope]

        # return pred_input
        return render_template("/prediction_result.html")

        # load the model from disk
        filename = 'model.pkl'
        load_model = joblib.load(filename)

        # append input here
        # age, sex, chest pain type, fasting blood sugar, max heart rate, exercise angine, oldpeak, ST slope
        pred_prob = load_model.predict([pred_input])
        predict = (pred_prob >= 0.35).astype(int).reshape(-1)

        return render_template("/prediction_result.html", prediction=predict, probability=pred_prob[0][0])
    else:
        return render_template("/heart-disease-prediction.html")


#    ------------ testing area ------------

# @app.route('/heart_diseases_prediction', methods=['POST', 'GET'])
# def heart_diseases_prediction():
#     # passing patient value
#     if request.method == 'POST':
#         hasil_hitungan = 0
#
#         for tipe_input in heart_diseases_input:
#             current_form_name = tipe_input[0]
#             current_form_value = request.form[current_form_name]
#             # handle null value
#             if current_form_value == '':
#                 print("null value on " + tipe_input)
#                 continue
#
#             # -------apply the model here---------
#             nilai = int(current_form_value)
#             hasil_hitungan = hasil_hitungan + nilai
#             # -------apply the model here---------
#
#         return "total csv adalah " + str(hasil_hitungan)
#
#     else:
#         # return render_template('/heart_diseases_prediction.html', inputs=heart_diseases_input)
#         return render_template('/heart_diseases_prediction.html',
#                                total_data=len(heart_diseases_input),
#                                input=heart_diseases_input)


# --set global variable for expert system
evidences = ['']
measurements = []
intolerance = ['']
infeasible = ['']
sex = ''
history = ''


@app.route('/expert_system', methods=['POST', 'GET'])
def expert_system():
    if request.method == 'POST':
        # --getting global variable
        global evidences
        global history
        global measurements
        global intolerance
        global infeasible
        global sex

        # --resting measurement value
        measurements = []

        # --getting value
        evidences = request.form.getlist('selected_evident')
        history = request.form.getlist('selected_history')
        intolerance = request.form.getlist('selected_intolerance')
        infeasible = request.form.getlist('selected_infeasible')
        sex = request.form.get('selected_sex')

        # --infeasible data fix
        if not infeasible:
            infeasible = ''

        # --getting measurement
        for i in range(6):
            current_measurement_value = request.form.get(expertSystem.measurement_input[i])
            if current_measurement_value == '':
                break

            measurements.append(
                {expertSystem.measurement_input[i]: int(current_measurement_value)}
            )

        # --merging history into evidence
        for current_history in history:
            evidences.append(current_history)

        # return [evidences,
        #         intolerance,
        #         infeasible,
        #         measurements]

        # testing_data = expertSystem.final_recommendations

        # initiate prolog
        prolog_final_result = expertSystem.generate_recommendation(evidences,
                                                                   measurements,
                                                                   intolerance,
                                                                   infeasible,
                                                                   sex)
        # return prolog_final_result
        # -- passing each type of recommendation
        recommendation_result = prolog_final_result[0]
        contraindications_result = prolog_final_result[1]
        no_benefits_result = prolog_final_result[2]

        return render_template('/expert_system_result.html',
                               recommendation_result=recommendation_result,
                               contraindications_result=contraindications_result,
                               no_benefits_result=no_benefits_result)

        # # return [recommendation_result, contraindications_result, no_benefits_result]
        #
        # results_arr = [recommendation_result, contraindications_result, no_benefits_result]

        # result_title = []
        # result_text = []
        # cor_level = []
        # loe_level = []
        # treatment_type = []
        #
        # for result in results_arr:
        #     for item in result:
        #         for key, values in item.items():
        #             result_title.append(key)
        #             for value in values:
        #                 result_text.append(value['text'])
        #                 cor_level.append(value['COR'])
        #                 loe_level.append(value['LOE'])
        #                 treatment_type.append(value['Type'])

        # return render_template('/expert_system_result.html',
        #                        result_title=result_title,
        #                        result_text=result_text,
        #                        cor_level=cor_level,
        #                        loe_level=loe_level,
        #                        treatment_type=treatment_type,
        #                        total_recommedation=len(recommendation_result),
        #                        total_contraindication=len(contraindications_result),
        #                        total_no_benefit=len(no_benefits_result))

        # return final_temp
    else:

        return render_template('/expert_system.html',
                               eveident_selection_value=expertSystem.evident_data_value,
                               eveident_selection_desc=expertSystem.evident_data_desc,
                               total_eveident_selection=len(expertSystem.evident_data_value),

                               infeasible_selection_value=expertSystem.infeasible_data_value,
                               infeasible_selection_desc=expertSystem.infeasible_data_desc,
                               total_infeasible_selection=len(expertSystem.infeasible_data_value),

                               history_selection_value=expertSystem.history_data_value,
                               history_selection_desc=expertSystem.history_data_desc,
                               total_history_selection=len(expertSystem.history_data_value),

                               intolearant_selection_value=expertSystem.intolerant_data_value,
                               intolearant_selection_desc=expertSystem.intolerant_data_desc,
                               total_intolearant_selection=len(expertSystem.intolerant_data_value),

                               measurement_value=expertSystem.measurement_input,
                               measurement_desc=expertSystem.measurement_desc,
                               total_measurement=len(expertSystem.measurement_input),

                               unmark_selection_value=expertSystem.unmarked_data_value,
                               unmark_selection_desc=expertSystem.unmarked_data_desc,
                               )


if __name__ == "__main__":
    def reshape(arr):
        return np.array(arr).reshape(-1, 1, arr.shape[1])


    app.run(debug=True)
