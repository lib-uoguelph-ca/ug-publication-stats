import logging
from models import Author

class UgAuthorUpdater:
    """
    Tries to match authors against LDAP entries.
    If a match is found, flag the author as a ug author and pull in some additional data like department and college.
    """

    # The LDAP directory doesn't contain colleges - only departments.
    # But for most academic units we can look up the college from the department name.
    # This dict provides that department - college mapping.
    dept_college = {
        'History': 'College of Arts',
        'Department of Philosophy': 'College of Arts',
        'School of English & Theatre Studies': 'College of Arts',
        'School of Fine Art & Music': 'College of Arts',
        'School of Languages & Literature': 'College of Arts',
        'Integrative Biology': 'College of Biological Sciences',
        'Molecular & Cellular Biology': 'College of Biological Sciences',
        'Human Health & Nutritional Science': 'College of Biological Sciences',
        'Department of Management': 'College of Business & Economics',
        'Economics and Finance': 'College of Business & Economics',
        'Marketing & Consumer Studies': 'College of Business & Economics',
        'School of Hospitality, Food and Tourism Management': 'College of Business & Economics',
        'Executive Programs': 'College of Business & Economics',
        'Chemistry': 'College of Physical & Engineering Science',
        'School of Computer Science (SOCS)': 'College of Physical & Engineering Science',
        'Mathematics & Statistics': 'College of Physical & Engineering Science',
        'Physics': 'College of Physical & Engineering Science',
        'Engineering': 'College of Physical & Engineering Science',
        'School of Engineering': 'College of Physical & Engineering Science',
        'Family Relations & Applied Nutrition': 'College of Social & Applied Human Sciences',
        'Geography, Environment and Geomatics': 'College of Social & Applied Human Sciences',
        'Psychology': 'College of Social & Applied Human Sciences',
        'Political Science': 'College of Social & Applied Human Sciences',
        'Sociology & Anthropology': 'College of Social & Applied Human Sciences',
        'International Development Studies': 'College of Social & Applied Human Sciences',
        'Food, Agricultural & Resource Economics': 'Ontario Agricultural College',
        'Department of Animal Biosciences': 'Ontario Agricultural College',
        'School of Environmental Sciences': 'Ontario Agricultural College',
        'Food Science': 'Ontario Agricultural College',
        'Dept of Plant Agriculture': 'Ontario Agricultural College',
        'Plant Agriculture': 'Ontario Agricultural College',
        'School of Environmental Design & Rural Development': 'Ontario Agricultural College',
        'Biomedical Science': 'Ontario Veterinary College',
        'Clinical Studies': 'Ontario Veterinary College',
        'Pathobiology': 'Ontario Veterinary College',
        'Population Medicine': 'Ontario Veterinary College'
    }

    def __init__(self, ldap_client):
        self.ldap_client = ldap_client
        self.logger = logging.getLogger('UGPS')

    def update_authors(self):
        """
        Loop through all authors and augment their records using information from the LDAP directory.
        :return:
        """
        authors = Author.select()

        for author in authors:
            self.logger.debug(f"Update Author: {author.first_name} {author.last_name}")
            if not author.first_name or not author.last_name:
                continue

            dept = self.ldap_client.get_department(author.first_name, author.last_name)
            if dept:

                college = None
                if dept in self.dept_college:
                    college = self.dept_college[dept]
                else:
                    self.logger.warning(f"Couldn't find college for department: {dept}")

                self.logger.debug(f"Found department for author: {author.first_name} {author.last_name}")
                author.local = True
                author.department = dept
                author.college = college
                author.save()