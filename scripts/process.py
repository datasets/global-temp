# -*- coding: utf-8 -*-

from __future__ import print_function

import logging

from re import match
from os import path, makedirs, listdir
from urllib2 import Request, urlopen
from datetime import datetime
from operator import itemgetter
from collections import OrderedDict
from json import dumps

try:
    from lxml import etree
except ImportError:
    etree = None

logger = logging.getLogger()

class SimpleFileCache():
    TAG_DELIMITER = '--'

    def __init__(self, directory):
        self.directory = directory
        if not path.exists(directory):
            makedirs(directory)

    def add(self, tags, ext, data):
        basename = self.TAG_DELIMITER.join(tags)
        file_name = '.'.join([basename, ext])
        destination = path.join(self.directory, file_name)
        with open(destination, 'w') as file:
            file.write(data)

    def findall(self):
        for file_name in listdir(self.directory):
            tags = path.splitext(file_name)[0].split(self.TAG_DELIMITER)
            source = path.join(self.directory, file_name)
            with open(source, 'r') as data:
                yield data, tags

class GISTEMP():
    def __init__(self):
        self.id = 'GISTEMP'
        self.name = 'GISS Surface Temperature Analysis (GISTEMP)'
        self.base_url = 'http://data.giss.nasa.gov/gistemp'
        self.source = OrderedDict([('name', self.name), ('web', self.base_url)])

    def retrieve(self):
        resource = '/'.join([self.base_url, 'tabledata_v3', 'GLB.Ts+dSST'])
        representation = 'txt'
        url = '.'.join([resource, representation])
        req = Request(url)
        res = urlopen(req)
        data = res.read()
        tags = [self.id.lower()]
        yield [data, tags, representation]

    def extract(self, data, tags):
        if tags[0] == self.id.lower():
            for row in self._extract_rows(data):
                yield self._extract_annual_row(data, row)
                for column in range(1, 13):
                    yield self._extract_monthly_row(data, row, column)

    def _extract_rows(self, data):
        for row in data:
            r = row.strip().split()
            if self._is_data_row(r):
                yield r

    def _extract_annual_row(self, data, row):
        year = row[0]
        mean = self._hundredths_degrees_to_degrees(row[13])
        annual_row = [self.id, year, mean]
        return ['annual', annual_row]

    def _extract_monthly_row(self, data, row, column):
        year = row[0]
        month = str(column).zfill(2)
        date = '-'.join([year, month])
        mean = self._hundredths_degrees_to_degrees(row[column])
        monthly_row = [self.id, date, mean]
        return ['monthly', monthly_row]

    def _is_data_row(self, row):
        return row and match(r'\d{4}', row[0])

    def _hundredths_degrees_to_degrees(self, hundredths_degrees):
        return str(int(hundredths_degrees)/100.0)

class GCAG():
    def __init__(self):
        self.id = 'GCAG'
        self.name = 'Global component of Climate at a Glance (GCAG)'
        self.base_url = 'http://www.ncdc.noaa.gov/cag/time-series/global'
        self.start_year = '1880'
        self.end_year = str(datetime.today().year)
        self.year_range = '-'.join([self.start_year, self.end_year])
        self.latitude_band = 'globe'
        self.surface = 'land_ocean'
        self.source = OrderedDict([('name', self.name), ('web', self.base_url)])

    def retrieve(self):
        source = self.id.lower()
        representation = 'csv'
        yield self._retrieve_annual(source, representation)
        for result in self._retrieve_monthly(source, representation):
            yield result

    def extract(self, data, tags):
        if tags[0] == self.id.lower():
            for year, mean in self._extract_rows(data):
                if match(r'\d{2}', tags[-1]):
                    month = tags[-1]
                    date = '-'.join([year, month])
                    row = [self.id, date, mean]
                    yield ['monthly', row]
                else:
                    row = [self.id, year, mean]
                    yield ['annual', row]

    def _retrieve_annual(self, source, representation):
        resource = self._get_resource('ytd', '12')
        url = '.'.join([resource, representation])
        data = self._get_data(url)
        tags = [source]
        return [data, tags, representation]

    def _retrieve_monthly(self, source, representation):
        for month in range(1, 13):
            m = str(month)
            resource = self._get_resource('1', m)
            url = '.'.join([resource, representation])
            data = self._get_data(url)
            tags = [source, m.zfill(2)]
            yield [data, tags, representation]

    def _get_resource(self, timescale, month):
        resource = '/'.join([
            self.base_url,
            self.latitude_band,
            self.surface,
            timescale,
            month,
            self.year_range
        ])
        return resource

    def _get_data(self, url):
        req = Request(url)
        res = urlopen(req)
        return res.read()

    def _extract_rows(self, data):
        for row in data:
            r = row.strip().split(',')
            if self._is_data_row(r):
                yield r

    def _is_data_row(self, row):
        return row and match(r'\d{4}', row[0])

class HadCRUT4():
    def __init__(self):
        self.id = 'HadCRUT4'
        self.name = 'Joint Met Office Hadley Centre and University of East Anglia HadCRUT global temperature dataset'
        self.home_url = 'http://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/download.html'
        self.base_url = 'http://www.metoffice.gov.uk/hadobs/hadcrut4/data/current'
        self.source = OrderedDict([('name', self.name), ('web', self.home_url)])

    def retrieve(self):
        for timescale, resource in self._get_resources():
            representation = resource.split('.')[-1]
            url = '/'.join([self.base_url, resource])
            data = self._get_data(url)
            tags = [self.id.lower(), timescale]
            yield [data, tags, representation]

    def extract(self, data, tags):
        if tags[0] == self.id.lower():
            timescale = tags[-1]
            for row in self._extract_rows(data):
                date = row[0].replace('/', '-') # does nothing if year only
                mean = row[1]
                yield [timescale, [self.id, date, mean]]

    def _get_resources(self):
        """Raise ValueError if lxml is not loaded"""
        if not etree:
            message = "lxml must be installed to use the HadCRUT4 processor"
            raise ValueError(message)

        data = self._get_data(self.home_url)
        html = etree.HTML(data)
        yield self._get_annual_resource(html)
        yield self._get_monthly_resource(html)

    def _get_annual_resource(self, html):
        result = html.xpath('//a[contains(@href, "annual_ns_avg.txt")]/@href')
        return ['annual', result[0]]

    def _get_monthly_resource(self, html):
        result = html.xpath('//a[contains(@href, "monthly_ns_avg.txt")]/@href')
        return ['monthly', result[0]]

    def _get_data(self, url):
        req = Request(url)
        res = urlopen(req)
        return res.read()

    def _extract_rows(self, data):
        for row in data:
            r = row.strip().split()
            if self._is_data_row(r):
                yield r

    def _is_data_row(self, row):
        return row and match(r'\d{4}', row[0])

class DataPackage():
    def __init__(self, fields, sources, resources):
        self.fields = fields
        self.fields.update([('sources', [source.source for source in sources])])
        self.fields.update([('resources', [resource for resource in resources])])

    def write(self):
        with open('datapackage.json', 'w') as file:
            file.write(dumps(self.fields, indent=2))

class DataProcessor():
    def __init__(self, sources):
        self.fields = OrderedDict()
        self.fields.update([('name', 'global-temp-time-series')])
        self.fields.update([('title', 'Global Temperature Anomalies Time Series')])
        self.fields.update([('version', '0.1.0')])
        self.fields.update([('license', 'PDDL-1.0')])

        self.sources = [source() for source in self._is_source(sources)]

        self.annual_fields = [OrderedDict(), OrderedDict(), OrderedDict()]
        self.annual_fields[0].update([('name', 'Source')])
        self.annual_fields[0].update([('type', 'string')])
        self.annual_fields[0].update([('description', '')])
        self.annual_fields[1].update([('name', 'Year')])
        self.annual_fields[1].update([('type', 'date')])
        self.annual_fields[1].update([('description', 'YYYY')])
        self.annual_fields[2].update([('name', 'Mean')])
        self.annual_fields[2].update([('type', 'number')])
        self.annual_fields[2].update([('description',
        u'Average mean temperature anomalies in °C relative to a base period.\n'
        'GISTEMP base period: 1951-1980\n'
        'GCAG base period: 20th century average\n'
        # 'HadCRUT4: 1961-1990'
        )])

        self.annual_schema = OrderedDict([('fields', self.annual_fields)])

        self.annual_resource = OrderedDict([])
        self.annual_resource.update([('name', 'annual')])
        self.annual_resource.update([('path', 'data/annual.csv')])
        self.annual_resource.update([('format', 'csv')])
        self.annual_resource.update([('mediatype', 'text/csv')])
        self.annual_resource.update([('schema', self.annual_schema)])

        self.monthly_fields = [OrderedDict(), OrderedDict(), OrderedDict()]
        self.monthly_fields[0].update([('name', 'Source')])
        self.monthly_fields[0].update([('type', 'string')])
        self.monthly_fields[0].update([('description', '')])
        self.monthly_fields[1].update([('name', 'Date')])
        self.monthly_fields[1].update([('type', 'date')])
        self.monthly_fields[1].update([('description', 'YYYY-MM')])
        self.monthly_fields[2].update([('name', 'Mean')])
        self.monthly_fields[2].update([('type', 'number')])
        self.monthly_fields[2].update([('description',
        u'Monthly mean temperature anomalies in °C relative to a base period.\n'
        'GISTEMP base period: 1951-1980\n'
        'GCAG base period: 20th century average'
        # 'HadCRUT4: 1961-1990'
        )])

        self.monthly_schema = OrderedDict([('fields', self.monthly_fields)])

        self.monthly_resource = OrderedDict([])
        self.monthly_resource.update([('name', 'monthly')])
        self.monthly_resource.update([('path', 'data/monthly.csv')])
        self.monthly_resource.update([('format', 'csv')])
        self.monthly_resource.update([('mediatype', 'text/csv')])
        self.monthly_resource.update([('schema', self.monthly_schema)])

        self.resources = [self.annual_resource, self.monthly_resource]

        if not path.exists('data'):
            makedirs('data')

    def setup(self):
        logger.info('Setting up processor')
        self.cache = SimpleFileCache('tmp')
        if not path.exists('data'):
            makedirs('data')

    def retrieve(self):
        for source in self.sources:
            logger.info('Retrieving %s data', source.id)
            for data, tags, representation in source.retrieve():
                self.cache.add(tags, representation, data)

    def extract(self):
        logger.info('Extracting data')
        annual_csv = self.annual_resource.get('path')
        monthly_csv = self.monthly_resource.get('path')
        annual_header = ','.join([
            field.get('name') for field in self.annual_fields
        ])
        monthly_header = ','.join([
            field.get('name') for field in self.monthly_fields
        ])
        with open(annual_csv, 'w') as annual, open(monthly_csv, 'w') as monthly:
            files = {'annual': annual, 'monthly': monthly}
            print(annual_header, file=annual)
            print(monthly_header, file=monthly)
            for data, tags in self.cache.findall():
                for source in self.sources:
                    for timescale, row in source.extract(data, tags):
                        print(','.join(row), file=files[timescale])

    def sort(self):
        logger.info('Sorting data')
        annual_csv = self.annual_resource.get('path')
        monthly_csv = self.monthly_resource.get('path')
        for file_path in [annual_csv, monthly_csv]:
            with open(file_path, 'r+') as file:
                data = [line.split(',') for line in file.read().splitlines()]
                header = data[0]
                sorted_data = sorted(data[1:], key=itemgetter(1), reverse=True)
                file.seek(0) # return to the top of the file
                print(','.join(header), file=file)
                for row in sorted_data:
                    print(','.join(row), file=file)

    def package(self):
        logger.info('Building data package')
        data_package = DataPackage(self.fields, self.sources, self.resources)
        data_package.write()

    def _is_source(self, sources):
        for source in sources:
            if source.__name__ in ['GISTEMP', 'GCAG', 'HadCRUT4']:
                yield source

def process():
    data_processor = DataProcessor([GISTEMP, GCAG])
    data_processor.setup()
    data_processor.retrieve()
    data_processor.extract()
    data_processor.sort()
    data_processor.package()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    process()
