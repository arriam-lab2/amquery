from amquery.core.distance import SamplePairwiseDistance, distances


class Factory:
    @staticmethod
    def create(config):
        """
        :param config: Config
        :return: PairWiseDistance 
        """
        method = config.get('distance', 'method')
        return SamplePairwiseDistance(distances[method])
