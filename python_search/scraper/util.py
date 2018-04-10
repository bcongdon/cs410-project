def format_month(month):
    """Formats a month for use in the mailing list URL

    Formats the month in the 'YYYY-MM' format
    
    Parameters
    ----------
    month : Date
        Any date in the desired month
    
    Returns
    -------
    str
        The formatted data
    """
    return month.strftime("%Y-%B")
