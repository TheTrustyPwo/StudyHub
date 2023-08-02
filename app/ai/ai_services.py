import datetime
import openai
import json
from flask import request, jsonify, Response
from flask_login import current_user, login_required

from app.ai import ai_api_blueprint, ai_services
from app.exceptions import BadRequest, Unauthorized, NotFound, Conflict
from app.models import User, Essay, EssayEvaluation, EssayCriticism, EssayCompliment


ESSAY_PROMPT = """pretend you are an english language student, given the following essay,
 i want you to evaluate in a completely fair way on how well written it is and provide both compilments as well as constructive critisism about the essay. Do not give too high evaluation. the compliments and criticisms should be in the form of a list.
  Return your evaluation in json in the exact format of
   {"evaluation": Poor/Fair/Satisfactory/Good/Very Good/Excellent, "compliments": [%compliment%, ...], "criticisms": [%criticism%, ...]}
    Do not index it, add numbers in front of each point or change anything."""


def grade_essay(topic: str, essay: str, user_id: int):
    prompt = ESSAY_PROMPT + "\nThe topic of the essay is: " + topic + "\n" + essay
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{"role": "system", "content": prompt}])
    print(response)
    graded = json.loads(response.choices[0].message.content.replace("\n", ""))

    print(graded)

    essay = Essay(topic, essay, EssayEvaluation(graded['evaluation'].lower()), user_id)
    essay.save()

    for remark in graded['compliments']:
        EssayCompliment(remark, essay.id).save()

    for remark in graded['criticisms']:
        EssayCriticism(remark, essay.id).save()

    return essay
