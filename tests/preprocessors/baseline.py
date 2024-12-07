from bluesky.preprocessors import SupplementalData, baseline_wrapper


# Define preprocesor for the baseline
class SupplementalDataBaseline(SupplementalData):
    def __init__(self, baseline, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseline = baseline

    def __call__(self, plan):
        plan = baseline_wrapper(plan, self.baseline)
        return (yield from plan)
