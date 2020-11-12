from __future__ import unicode_literals
import argparse
from cadcutils import exceptions
import numpy
from cadcutils import net
from caom2 import *
from astropy import time
from astropy import units, constants
import logging
import os
from caom2repo import CAOM2RepoClient
import math
import pickle
from astroquery.alma import Alma

# Create a CAOM2RepoClient object.
certificate = os.path.join(os.getenv('HOME'), '.ssl/cadcproxy.pem')
resource_id = 'ivo://cadc.nrc.ca/sc2repo'
repo_client = CAOM2RepoClient(net.Subject(certificate=certificate), resource_id=resource_id)


def nan2None(x):
    return not numpy.isnan(x) and x or None


def build_position(ra, dec, radius=24*units.arcsec):

    points = []
    vertices = []
    segment_type = SegmentType['MOVE']
    x1 = y1 = None
    for theta in range(360, 0, -5):
        x = radius.to('degree').value*math.cos(math.radians(theta)) + ra
        y = radius.to('degree').value*math.sin(math.radians(theta)) + dec
        points.append(Point(x, y))
        vertices.append(Vertex(x, y, segment_type))
        segment_type = SegmentType['LINE']
        if x1 is None:
            x1 = x
            y1 = y

    # Close up the sample area
    vertices.append(Vertex(x1,
                           y1,
                           SegmentType['CLOSE']))

    return Position(bounds=Polygon(points=points, samples=shape.MultiPolygon(vertices)),
                    sample_size=None,
                    time_dependent=False)


def build_energy(spectral_windows):

    energy = Energy()
    energy.em_band = EnergyBand.MILLIMETER
    energy.dimension = 1
    c = constants.c.to('m/s').value

    samples = []
    wvlns = []
    mid_wvln = []
    min_wvln = 1e10
    max_wvln = 0
    for spw in spectral_windows:
        wvln = numpy.array((c/spw[0], c/spw[1]))
        wvlns.append(wvln)
        mid_wvln.append(wvln[0]+wvln[1])
    order = numpy.argsort(mid_wvln)

    for idx in order:
        interval = shape.SubInterval(min(wvlns[idx]), max(wvlns[idx]))
        samples.append(interval)
        min_wvln = min(min_wvln, min(wvlns[idx]))
        max_wvln = max(max_wvln, max(wvlns[idx]))


    # Build the energy bounds
    energy.bounds = Interval(min_wvln, max_wvln, samples=samples)

    return energy


def build_time(start_date, end_date, exposure_time):
    time_bounds = Interval(start_date,
                           end_date,
                           samples=[shape.SubInterval(start_date, end_date)])
    return Time(bounds=time_bounds,
                dimension=1,
                resolution=exposure_time.to('second').value,
                sample_size=exposure_time.to('day').value,
                exposure=exposure_time.to('second').value
                )


def build_observation(override):
    """

    :type override: dict
    """


    release_date = time.Time(overrides['release_date']).to_datetime()

    telescope = Telescope(name="ALMA-12m",
                          geo_location_x=2225142.18,
                          geo_location_y=-5440307.37,
                          geo_location_z=-2481029.852
                          )

    instrument = Instrument(name="Band {}".format(override['band']))

    target = Target(name=override['target_name'],
                    standard=False,
                    moving=False,
                    target_type=TargetType.OBJECT,
                    )

    proposal = Proposal(id=override['project_id'],
                        pi_name=override['pi_name'],
                        title=override['project_title'])

    proposal.keywords = set(overrides['keywords'].split())

    observation = SimpleObservation(collection="ALMA",
                                    observation_id=override['observation_id'],
                                    sequence_number=None,
                                    intent=ObservationIntentType.SCIENCE,
                                    type="OBJECT",
                                    proposal=proposal,
                                    telescope=telescope,
                                    instrument=instrument,
                                    target=target,
                                    meta_release=time.Time("2018-01-01T00:00:00").to_datetime()
                                    )

    provenance = Provenance(name="CASA",
                            version="{}".format(override['casa_version']),
                            last_executed=time.Time(override['casa_run_date']).datetime,
                            reference="https://casa.nrao.edu/")

    artifact = Artifact(uri=override['artifact_uri'],
                        product_type=ProductType.SCIENCE,
                        release_type=ReleaseType.DATA,
                        content_type=None,
                        content_length=None)

    plane = Plane(product_id="measurement_set",
                  data_release=release_date,
                  meta_release=release_date,
                  provenance=provenance)

    plane.position = build_position(override['ra'], override['dec'])
    plane.energy = build_energy(override['spectral_windows'])
    plane.polarization = None
    plane.time = build_time(override['start_date'], override['end_date'], override['exposure_time']*units.second)
    plane.data_product_type = DataProductType.IMAGE
    plane.calibration_level = CalibrationLevel.CALIBRATED

    plane.artifacts.add(artifact)

    observation.planes.add(plane)

    # And the plane to the observation.
    observation.planes.add(plane)
    return observation


def caom2repo(this_observation):
    """
    Put an observation into the CAOM repo service

    :param this_observation: the CAOM2 Python object to store to caom2repo service
    :return:
    """

    try:
        logging.info('Inserting observation {}'.format(this_observation.observation_id))
        repo_client.put_observation(this_observation)
    except exceptions.AlreadyExistsException as ex:
        logging.info('Deleting observation {}'.format(this_observation.observation_id))
        repo_client.delete_observation(this_observation.collection, this_observation.observation_id)
        logging.info('Inserting observation {}'.format(this_observation.observation_id))
        repo_client.put_observation(this_observation)


def main(override):

    observation = build_observation(override)

    with open(str('junk.xml'), str('w')) as fobj:
        ObservationWriter().write(observation, fobj)
    caom2repo(observation)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Populate CAOM2 database with ALMA Measurement Set MD.")
    parser.add_argument("project_id")
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    log_level = logging.ERROR
    if args.verbose:
        log_level = logging.INFO
    elif args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)

    md = pickle.load(open("{}_md.pk".format(args.project_id)))

    db_table = Alma().query(payload={'project_code': args.project_id})

    overrides={}
    overrides['pi_name'] = db_table['PI name'][0]
    overrides['project_title'] = db_table['Project title'][0]
    overrides['casa_version'] = "4.7.2"
    overrides['casa_run_date'] = "2018-05-17T00:00:00"
    overrides['release_date']  = db_table['Release date'][0]
    overrides['project_id'] = args.project_id
    overrides['keywords']  = db_table['Science keyword'][0]

    for artifact in md.keys():

        overrides['observation_id'] = artifact.rstrip('.ms.split.cal')
        overrides['target_name'] = md[artifact]['field']
        overrides['ra'] = md[artifact]['ra']
        overrides['dec'] = md[artifact]['dec']
        overrides['start_date'] = md[artifact]['start_date']
        overrides['end_date'] = md[artifact]['end_date']
        overrides['exposure_time'] = md[artifact]['itime']
        overrides['artifact_uri'] = "ad:ALMA/{}.tgz".format(artifact)
        overrides['product_id'] = "ms.split.cal"
        overrides['band'] = md[artifact]['band']
        overrides['spectral_windows'] = md[artifact]['spectral_windows']
        main(overrides)
