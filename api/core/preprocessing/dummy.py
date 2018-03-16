from api.core.preprocessing import Preprocessor


class DummyPreprocessor(Preprocessor):
    def __call__(self, sample):
        """
        :param sample: Sample 
        :return: Sample
        """
        return sample