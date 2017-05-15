import abc


class Preprocessor:
    @abc.abstractmethod
    def __call__(self, sample):
        """
        :param sample: Sample 
        :return: Sample
        """
        return sample
