import abc


class Storage:
    @abc.abstractmethod
    def build(self, collection):
        """
        :param collection: SampleCollection 
        :return: Boolean
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def find(self, sample_ref, k):
        """
        :param sample_ref: SampleReference
        :param k: int
        :return: Sequence[SampleReference]
        """
        raise NotImplementedError()

    @abc.abstractstaticmethod
    def create(self, config):
        """
        :param config: Config
        :return: MetricIndexStorage 
        """
        raise NotImplementedError()
