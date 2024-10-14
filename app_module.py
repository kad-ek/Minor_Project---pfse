from handcalcs.decorator import handcalc


@handcalc()
def calc_Mr2(Sx: float, Fy: float, gamma: float = 1.1):
    """
    Calculates Mr of a rectangular section
    """
    M_r = Sx * Fy / gamma
    return M_r