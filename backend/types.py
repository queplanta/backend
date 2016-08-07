from graphene.relay.types import Connection as GrapheneRelayConnection


class RelayConnection(GrapheneRelayConnection):
    def _set_parent(self, parent):
        self._parent = parent
