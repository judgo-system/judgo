
from judgment.models import PreferenceJudgmentChoices
from interfaces import pref



def highlight_document(text, highlight):
    """
    """
    if not highlight:
        return text
    highlights = highlight.split("|||")

    for part in highlights:
        if part:
            text = text.replace(part, "<span class = 'highlight'>{}</span>".format(part))
    return text



def add_new_answer(state, task):
    best_docs = pref.get_best(state)

    prev_ans = task.best_answers if task.best_answers else "" 
    new_ans = ""

    for doc in best_docs:
        new_ans += doc + "|"

    task.best_answers = prev_ans +"--"+new_ans
    task.num_ans = len(task.best_answers.split("|")) - 1
    task.save()

    return best_docs

def evaluate_after_state(requested_action, before_state):
        """
        """
        action, after_state = None, None

        (left, right) = pref.get_documents(before_state)

        if 'left' in requested_action:
            action = PreferenceJudgmentChoices.LEFT
            after_state = pref.evaluate(before_state, left)
        elif 'right' in requested_action:
            action = PreferenceJudgmentChoices.RIGHT
            after_state = pref.evaluate(before_state, right)
        else:
            action = PreferenceJudgmentChoices.EQUAL
            after_state = pref.evaluate(before_state, right, equal=True)
        
        return action, after_state
