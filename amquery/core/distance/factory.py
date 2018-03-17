from amquery.core.distance import SamplePairwiseDistance, distances


class Factory:
    @staticmethod
    def create(database_config):
        """
        :param database_config: dict
        :return: PairwiseDistance 
        """
        method = database_config["distance"]
        return SamplePairwiseDistance(distances[method](database_config))

    @staticmethod
    def load(database_config):
        """
        :param database_config: dict
        :return: PairWiseDistance 
        """
        return SamplePairwiseDistance.load(database_config)
