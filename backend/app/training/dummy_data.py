"""app/training/dummy_data.py – Aggregated Q&A pairs and documentation per instance.

Imports module-specific training data from individual files.
"""

from app.training.it_meetingsphere_data import IT_MEETINGSPHERE_TRAINING
from app.training.it_cdxp_data import IT_CDXP_TRAINING
from app.training.it_lcm_data import IT_LCM_TRAINING
from app.training.it_pop_data import IT_POP_TRAINING

DUMMY_TRAINING: dict[str, dict] = {
    "it_meetingsphere": IT_MEETINGSPHERE_TRAINING,
    "it_cdxp": IT_CDXP_TRAINING,
    "it_lcm": IT_LCM_TRAINING,
    "it_pop": IT_POP_TRAINING,
}
