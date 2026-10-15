from . import pushups, squats, jumping_jacks, situps, lunges

EXERCISES = {
    pushups.NAME: pushups.logic,
    squats.NAME: squats.logic,
    jumping_jacks.NAME: jumping_jacks.logic,
    situps.NAME: situps.logic,
    lunges.NAME: lunges.logic,
}


def get(name):
    return EXERCISES[name]
