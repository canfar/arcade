from astroquery.alma import AlmaClass


class CADCAlmaClass(AlmaClass):

    def query_obsdate_async(self, oldest_observation, newest_observation, cache=True, public=True,
                            science=False, payload=None, **kwargs):
        """
        Query the archive within a given observation date range.

        Parameters
        ----------
        oldest_observation : Time
            The oldest data set to include in result set.
        newest_observation : Time
            The most recent data set to include in result set.
        cache : bool
            Cache the query?
        public : bool
            Return only publicly available datasets?
        science : bool
            Return only data marked as "science" in the archive?
        payload : dict
            Dictionary of additional keywords.  See `help`.
        kwargs : dict
            Passed to `query_async`
        """

        if payload is None:
            payload = {}
        d1 = oldest_observation.to_datetime().timetuple()
        d2 = newest_observation.to_datetime().timetuple()
        payload.update({'start_date': "{:02d}-{:02d}-{:4d} .. {:02d}-{:02d}-{:4d}".format(d1.tm_mday, d1.tm_mon, d1.tm_year,
                                                                  d2.tm_mday, d2.tm_mon, d2.tm_year)})
        #print payload
        return self.query_async(payload, cache=cache, public=public,
                                science=science, **kwargs)


if __name__ == "__main__":
    from astropy.time import Time
    oldest_data = Time("2009-01-01 10:00:00", out_subfmt='date')
    newest_data = Time("2019-12-31 10:00:00", out_subfmt='date')
    with open('result.vot','wb') as fout:
       fout.write(CADCAlmaClass().query_obsdate_async(oldest_data, newest_data).content)
