/** Category index from CMS India Resources for Researchers — URLs unchanged. */

export const CMS = "https://www.thecmsindia.org";

export const CMS_RESEARCH = `${CMS}/resources/resources-for-researchers`;

export const CMS_LETTER_INDEX = "abcdefghijklmnopqrstuvwxyz".split("").map((letter) => ({
  letter: letter.toUpperCase(),
  href: `${CMS}/projects/resources-for-researchers/jfilter-menu-${letter}`,
}));

export type ResearchLang = "syriac" | "malayalam" | "english";

export type ResearchItem = {
  title: string;
  href?: string;
};

export type ResearchGroup = {
  title: string;
  href?: string;
  items: ResearchItem[];
};

export type ResearchSection = {
  id: ResearchLang;
  label: string;
  groups: ResearchGroup[];
};

function tag(slug: string) {
  return `${CMS}/projects/resources-for-researchers/jfilter-menutag-${slug}`;
}

export const RESEARCH_SECTIONS: ResearchSection[] = [
  {
    id: "syriac",
    label: "Syriac",
    groups: [
      {
        title: "Syriac Language and Grammar",
        items: [
          { title: "Syriac Grammar", href: tag("syriac-grammar") },
          { title: "Syriac Dictionary", href: tag("syriac-dictionary") },
          { title: "Syriac Manuscripts", href: tag("syriac-manuscripts") },
          { title: "Syriac Books" },
        ],
      },
      {
        title: "Syriac Liturgical Books",
        items: [
          { title: "Syriac Thaksa", href: tag("syriac-thaksa") },
          { title: "Hudra", href: tag("syriac-hudra") },
          { title: "Peshitta Bible", href: tag("syriac-peshitta-bible") },
          {
            title: "Holy Qurbana in Syriac",
            href: tag("holy-qurbana-in-syriac"),
          },
          { title: "Holy Sacrements in Syriac" },
        ],
      },
      {
        title: "Syriac Songs and Poems",
        items: [],
      },
      {
        title: "Syriac Non Liturgical Books",
        items: [
          { title: "Funeral Services for Bishops" },
          {
            title: "Funeral Services for Priests",
            href: tag("funeral-services-priests"),
          },
          {
            title: "Funeral Services for Layman",
            href: tag("funeral-services-layman"),
          },
        ],
      },
    ],
  },
  {
    id: "malayalam",
    label: "Malayalam",
    groups: [
      {
        title: "Malayalam Manuscripts",
        items: [],
      },
      {
        title: "Malayalam Liturgical Books",
        items: [
          { title: "Thaksa in Malayalam — തക്സ" },
          {
            title: "Holy Qurbana in Malayalam — വിശുദ്ധ കുർബാന",
            href: tag("holy-qurbana-in-malayalam"),
          },
        ],
      },
      {
        title: "Malayalam Songs and Poems",
        href: tag("malayalam-songs-and-poems"),
        items: [],
      },
      {
        title: "Malayalam Non Liturgical Books",
        items: [
          {
            title: "Church History — സഭാ ചരിത്രം",
            href: tag("church-history-in-malayalam"),
          },
          {
            title: "Articles and Publications — ലേഖനങ്ങളും പ്രസിദ്ധീകരണങ്ങളു",
            href: tag("publications-in-malayalam"),
          },
        ],
      },
    ],
  },
  {
    id: "english",
    label: "English",
    groups: [
      {
        title: "English Liturgical Books",
        items: [
          { title: "English Thaksa" },
          {
            title: "Solemn High Mass in English",
            href: tag("solemn-high-mass-in-english"),
          },
        ],
      },
      {
        title: "English Non Liturgical Books",
        items: [
          { title: "Ethnomusicology" },
          {
            title: "Church History",
            href: tag("church-history-in-english"),
          },
          {
            title: "Research articles and Publications",
            href: tag("research-articles-and-publications"),
          },
          { title: "Christian Art", href: tag("christian-art") },
          { title: "Personality", href: tag("personality") },
        ],
      },
    ],
  },
];

export const CMS_RELATED = [
  { title: "Digital Library", href: `${CMS}/projects/digital-library` },
  { title: "Aramaic Project", href: `${CMS}/aramaic-project` },
  {
    title: "Encyclopedia of Syriac Chants",
    href: `${CMS}/encyclopedia-of-syriac-chants`,
  },
  {
    title: "Directory of Christian Songs",
    href: `${CMS}/directory-of-christian-songs`,
  },
  {
    title: "Christian Art / Music Iconography",
    href: `${CMS}/projects/christian-art-music-iconography`,
  },
  {
    title: "Resources AP Videos",
    href: `${CMS}/resources/resource-ap-videos`,
  },
];

export const CMS_LISTING = `${CMS}/resources/resources-for-researchers/admin-listing-page`;
export const CMS_REGISTER = `${CMS}/component/users/registration?Itemid=101`;
export const CMS_RECENT = {
  title: "A-hymn-for-evening-prayer-on-Good-Friday",
  href: `${CMS_RESEARCH}/no-1500-to-1451/a-hymn-for-evening-prayer-on-good-friday`,
  range: "No 1500 to 1451",
  date: "27 Aug 2025",
};
