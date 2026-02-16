import logging

logger = logging.getLogger(__name__)


class DemocraticCore:
    """Minimal stub for DemocraticCore to allow boot when real module is absent.
    Replace with full implementation for production use.
    """

    def __init__(self, core):
        logger.warning("Using DemocraticCore stub — full implementation not present.")
        self.core = core

    def initialize(self):
        logger.info("DemocraticCore stub initialize called — no-op")

    def shutdown(self):
        logger.info("DemocraticCore stub shutdown called — no-op")
