import json
from decimal import Decimal
import unittest

from tigershark.facade import f271
from tigershark.parsers.M271_5010_X279_A1 import parsed_271


class TestParsed271(unittest.TestCase):
    def setUp(self):
        with open('tests/samples/5010-271-1.txt') as f:
            parsed = parsed_271.unmarshall(f.read().strip())
        self.facade = f271.F271_5010(parsed).facades[0]

    def test_financial_information(self):
        eobi = self.facade.subscribers[0].eligibility_or_benefit_information
        self.assertEqual(
            eobi[0].coverage_information.service_type,
            ('30', 'Health Benefit Plan Coverage'))
        self.assertEqual(
            eobi[0].coverage_information.insurance_type,
            ('EP', 'Exclusive Provider Organization'))
        self.assertEqual(eobi[0].coverage_information.description, '')
        self.assertEqual(eobi[1].coverage_information.benefit_amount, Decimal(0))
        self.assertEqual(eobi[1].coverage_information.benefit_percent, Decimal(0))
        self.assertEqual(eobi[1].coverage_information.information_type,
                         ('W', 'Other Source of Data'))

    def test_repetition_separator(self):
        eobi = self.facade.subscribers[0].eligibility_or_benefit_information
        information = eobi[8]  # multiple types
        information_types = information.coverage_information.service_type
        expected_types = [
            ('1', 'Medical Care'),
            ('33', 'Chiropractic'),
            ('47', 'Hospitalization'),
            ('48', 'Hospital - Inpatient'),
            ('50', 'Hospital - Outpatient'),
            ('86', 'Emergency Services'),
            ('98', 'Professional (Physician) Visit - Office'),
            ('UC', 'Urgent Care'),
            ('AL', 'Optometry'),
            ('MH', 'Mental Health'),
            ('88', 'Pharmacy'),
            ]
        self.assertListEqual(information_types, expected_types)

    def test_subscriber_information(self):
        subscriber = self.facade.subscribers[0]
        location = subscriber.personal_information.address_location
        self.assertEqual(location.city, 'KANSAS CITY')
        self.assertEqual(location.state, 'MO')
        self.assertEqual(location.zip, '64108')
        street = subscriber.personal_information.address_street
        self.assertEqual(street.addr1, '4040 VILLAGE AB')
        self.assertEqual(street.addr2, '')
        dates = subscriber.personal_information.dates
        self.assertEqual(dates[0].time.strftime('%Y-%m-%d'), '2016-02-01')
        self.assertEqual(dates[0].type, ('346', 'Plan Begin'))
        self.assertEqual(dates[1].time.strftime('%Y-%m-%d'), '2016-06-01')
        self.assertEqual(dates[1].type, ('472', 'Service'))
        self.assertEqual(dates[2].time.strftime('%Y-%m-%d'), '2014-12-08')
        self.assertEqual(dates[2].type, ('356', 'Eligibility Begin'))
        demographic = subscriber.personal_information.demographic_information
        self.assertEqual(demographic.birth_date.strftime('%Y-%m-%d'), '1943-08-13')
        self.assertEqual(demographic.gender, ('M', 'Male'))
        name = subscriber.personal_information.name
        self.assertEqual(name.entity_identifier, ('IL', 'Insured'))
        self.assertEqual(name.entity_type, ('1', 'Person'))
        self.assertEqual(name.first_name, 'JOHN')
        self.assertEqual(name.id_code, '1234567899')
        self.assertEqual(name.id_code_qual, ('MI', 'Member Identification Number'))
        self.assertEqual(name.last_name, 'SMITH')
        self.assertTrue(name.is_person)
        reference_ids = subscriber.personal_information.reference_ids
        self.assertEqual(reference_ids[0].reference_id, '0404044')
        self.assertEqual(reference_ids[0].reference_id_qualifier, ('18', 'Plan Number'))
        self.assertEqual(reference_ids[1].reference_id, '030030001000120')
        self.assertEqual(reference_ids[1].reference_id_qualifier, ('6P', 'Group Number'))
        self.assertEqual(reference_ids[1].description, 'NEVADA EXCHANGE')
        relationship = subscriber.personal_information.relationship
        self.assertTrue(relationship.is_insured)
        self.assertEqual(relationship.maintenance_reason, ('25', 'Change in Identifying Data Elements'))
        self.assertEqual(relationship.maintenance_type, ('001', 'Change'))
        self.assertEqual(relationship.relationship, ('18', 'Self'))

    def test_receiver(self):
        r_name = self.facade.receivers[0].receiver_information.name
        self.assertEqual(r_name.entity_identifier, ('1P', 'Provider'))
        self.assertEqual(r_name.entity_type, ('1', 'Person'))
        self.assertEqual(r_name.first_name, 'Barraret')
        self.assertEqual(r_name.id_code, '1234567894')
        self.assertEqual(r_name.id_code_qual,
             ('XX', 'Health Care Financing Administration National Provider Identifier'))
        self.assertTrue(r_name.is_person)
        self.assertEqual(r_name.middle_initial, 'J.')
        self.assertEqual(r_name.last_name, 'James')

    def test_version(self):
        self.assertEqual(self.facade.transaction_set_identifier_code, '271')
        self.assertEqual(self.facade.x12_version_string, '5010')

    def test_payer(self):
        eobi = self.facade.subscribers[0].eligibility_or_benefit_information
        benefit_related_entity = eobi[1].benefit_related_entity
        self.assertEqual(benefit_related_entity.address_location.city, 'El Fixato')
        self.assertEqual(benefit_related_entity.address_location.state, 'TX')
        self.assertEqual(benefit_related_entity.address_location.zip, '68887')
        self.assertEqual(benefit_related_entity.address_street.addr1, 'PO Box 983322')
        self.assertEqual(benefit_related_entity.name.entity_identifier, ('PR', 'Payer'))
        self.assertEqual(benefit_related_entity.name.entity_type,
                         ('2', 'Non-Person Entity'))
        self.assertTrue(benefit_related_entity.name.is_organization)
        self.assertEqual(benefit_related_entity.name.org_name, 'Mala Compania')

    def test_header(self):
        header = self.facade.header
        self.assertIsNone(header)

    def test_coverage_information_list(self):
        self.facade = None
        with open('tests/samples/5010-271-3.txt') as f:
            content = f.read().strip()
        parsed = parsed_271.unmarshall(content)
        facades = f271.F271_5010(parsed).facades
        self.assertEqual(1, len(facades))
        self.assertEqual(1, len(facades[0].subscribers))

        eobi = facades[0].subscribers[0].eligibility_or_benefit_information
        self.assertEqual(26, len(eobi))
        self.assertEqual(('30', 'Health Benefit Plan Coverage'),
                         eobi[0].coverage_information.service_type)
        self.assertEqual('Open Record', eobi[0].coverage_information.description)
        self.assertListEqual(['ABC+'], eobi[0].messages)

        self.assertEqual(Decimal('0'), eobi[1].coverage_information.benefit_amount)
        self.assertEqual(Decimal('0.3'), eobi[1].coverage_information.benefit_percent)
        self.assertTupleEqual(('IND', 'Individual'), eobi[1].coverage_information.coverage_level)
        self.assertTrue(eobi[1].coverage_information.in_plan_network)
        self.assertEqual('2016-04-26', str(eobi[1].dates[0].time))
        self.assertTupleEqual(('348', 'Benefit Begin'), eobi[1].dates[0].type)
        self.assertListEqual(["THIS BENEFIT DOES APPLY TO MEMBER'S OUT-OF-POCKET PREMIUM"],
                             eobi[1].messages)

        self.assertEqual(Decimal('2500'), eobi[2].coverage_information.benefit_amount)
        self.assertEqual(Decimal('0'), eobi[2].coverage_information.benefit_percent)
        self.assertTupleEqual(('IND', 'Individual'), eobi[2].coverage_information.coverage_level)
        self.assertFalse(eobi[2].coverage_information.both_in_out_network)
        self.assertTrue(eobi[2].coverage_information.in_plan_network)
        self.assertTupleEqual(('C', 'Deductible'), eobi[2].coverage_information.information_type)
        self.assertTupleEqual(('23', 'Calendar Year'),
                              eobi[2].coverage_information.time_period_type)
        self.assertListEqual([], eobi[2].dates)
        self.assertEqual(('30', 'Health Benefit Plan Coverage'),
                         eobi[2].coverage_information.service_type)
        self.assertListEqual([
            "BENEFIT DOES APPLY TO MEMBER'S OUT-OF-POCKET PREMIUM",
            'OUT OF NETWORK AMOUNTS APPLY TO IN-NETWORK',
            'ACCUMULATORS ARE SHARED BETWEEN MEDICAL AND PHARMACY'
        ], eobi[2].messages)

        self.assertListEqual([], eobi[14].additional_information)
        self.assertEqual(Decimal('0.4'), eobi[14].coverage_information.benefit_percent)
        self.assertTupleEqual(('FAM', 'Family'), eobi[14].coverage_information.coverage_level)
        self.assertTupleEqual(('A', 'Co-Insurance'),
                              eobi[14].coverage_information.information_type)
        self.assertEqual('2016-04-26', str(eobi[14].dates[0].time))
        self.assertTupleEqual(('348', 'Benefit Begin'), eobi[14].dates[0].type)
        self.assertEqual(('86', 'Emergency Services'),
                         eobi[14].coverage_information.service_type)
        self.assertListEqual([
            'BEHAVIORAL',
            "THIS BENEFIT DOES APPLY TO MEMBER'S OUT-OF-POCKET PREMIUM",
            'MEDICAL'], eobi[14].messages)

    def test_referral_request_for_review(self):
        self.facade = None
        with open('tests/samples/5010-271-4.txt') as f:
            content = f.read().strip()
        parsed = parsed_271.unmarshall(content)
        facades = f271.F271_5010(parsed).facades
        self.assertEqual(1, len(facades))
        self.assertEqual(1, len(facades[0].subscribers))
        # TODO:  write more asserts

    def test_error_payer_not_supported(self):
        """
        Have
        """
        self.facade = None
        with open('tests/samples/5010-271-5.txt') as f:
            content = f.read().strip()
        parsed = parsed_271.unmarshall(content)
        facades = f271.F271_5010(parsed).facades
        self.assertEqual(1, len(facades))

#        print json.dumps(facades[0].get_representation(), indent=4)


        self.assertEqual(0, len(facades[0].subscribers))
        # TODO: check and describe, write more asserts

if __name__ == "__main__":
    unittest.main()
