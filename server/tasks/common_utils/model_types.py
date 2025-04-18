import pendulum
from pydantic import BaseModel, ConfigDict


class ExtraModel(BaseModel):
    """Include untyped keys in object attributes"""

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True
    )


class Namelist(ExtraModel):
    stilt_wd: str
    n_cores: int = 4
    t_start: pendulum.DateTime
    t_end: pendulum.DateTime
    lati: float
    long: float
    zagl: int
    xmn: float
    xmx: float
    ymn: float
    ymx: float
    xres: float
    yres: float
