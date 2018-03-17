from amquery.core.storage import VpTree


class Factory:
    @staticmethod
    def create(database_config):
        """
        :param config: Config
        :return: Storage
        """
        return VpTree()

    @staticmethod
    def load(database_config):
        """
        :param config: Config
        :return: Storage
        """
        database_name = database_config["name"]
        return VpTree.load(database_name)
