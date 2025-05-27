"""[dashboard] remove unused synthese materialized view

Revision ID: 58f1612ce31d
Revises: 9a9ef04f6010
Create Date: 2025-05-19 10:55:19.142168

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "58f1612ce31d"
down_revision = "9a9ef04f6010"
branch_labels = None
depends_on = ("d73f74e7b662",)


def upgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS gn_dashboard.vm_taxonomie")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS gn_dashboard.vm_synthese")
    op.execute(
        """
        CREATE MATERIALIZED VIEW gn_dashboard.vm_taxonomie
    TABLESPACE pg_default
    AS SELECT 'Règne'::text AS level,
        COALESCE(gn_synthese.v_synthese_for_web_app.regne, 'Not defined'::character varying) AS name_taxon
    FROM gn_synthese.v_synthese_for_web_app
    GROUP BY gn_synthese.v_synthese_for_web_app.regne
    UNION ALL
    SELECT 'Phylum'::text AS level,
        COALESCE(gn_synthese.v_synthese_for_web_app.phylum, 'Not defined'::character varying) AS name_taxon
    FROM gn_synthese.v_synthese_for_web_app
    GROUP BY gn_synthese.v_synthese_for_web_app.phylum
    UNION ALL
    SELECT 'Classe'::text AS level,
        COALESCE(gn_synthese.v_synthese_for_web_app.classe, 'Not defined'::character varying) AS name_taxon
    FROM gn_synthese.v_synthese_for_web_app
    GROUP BY gn_synthese.v_synthese_for_web_app.classe
    UNION ALL
    SELECT 'Ordre'::text AS level,
        COALESCE(gn_synthese.v_synthese_for_web_app.ordre, 'Not defined'::character varying) AS name_taxon
    FROM gn_synthese.v_synthese_for_web_app
    GROUP BY gn_synthese.v_synthese_for_web_app.ordre
    UNION ALL
    SELECT 'Famille'::text AS level,
        COALESCE(gn_synthese.v_synthese_for_web_app.famille, 'Not defined'::character varying) AS name_taxon
    FROM gn_synthese.v_synthese_for_web_app
    GROUP BY gn_synthese.v_synthese_for_web_app.famille
    UNION ALL
    SELECT 'Groupe INPN 1'::text AS level,
        COALESCE(gn_synthese.v_synthese_for_web_app.group1_inpn, 'Not defined'::character varying) AS name_taxon
    FROM gn_synthese.v_synthese_for_web_app
    GROUP BY gn_synthese.v_synthese_for_web_app.group1_inpn
    UNION ALL
    SELECT 'Groupe INPN 2'::text AS level,
        COALESCE(gn_synthese.v_synthese_for_web_app.group2_inpn, 'Not defined'::character varying) AS name_taxon
    FROM gn_synthese.v_synthese_for_web_app
    GROUP BY gn_synthese.v_synthese_for_web_app.group2_inpn
    UNION ALL
    SELECT 'Groupe INPN 3'::text AS level,
        COALESCE(gn_synthese.v_synthese_for_web_app.group3_inpn, 'Not defined'::character varying) AS name_taxon
    FROM gn_synthese.v_synthese_for_web_app
    GROUP BY gn_synthese.v_synthese_for_web_app.group3_inpn
    WITH DATA;
    CREATE UNIQUE INDEX vm_taxonomie_name_taxon_level_idx ON gn_dashboard.vm_taxonomie USING btree (name_taxon, level);
"""
    )


def downgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS gn_dashboard.vm_taxonomie")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS  gn_dashboard.vm_synthese")
    op.execute(
        """
        CREATE MATERIALIZED VIEW gn_dashboard.vm_synthese
    TABLESPACE pg_default
    AS SELECT s.id_synthese,
    s.id_source,
    s.id_dataset,
    s.id_nomenclature_obj_count,
    s.count_min,
    s.count_max,
    s.cd_nom,
    t.cd_ref,
    s.nom_cite,
    t.id_statut,
    t.id_rang,
    t.regne,
    t.phylum,
    t.classe,
    t.ordre,
    t.famille,
    t.sous_famille,
    t.group1_inpn,
    t.group2_inpn,
    t.group3_inpn,
    t.lb_nom,
    t.nom_vern,
    t.url,
    s.altitude_min,
    s.altitude_max,
    s.date_min,
    s.date_max
    FROM gn_synthese.synthese s
        JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
    WITH DATA;

    CREATE INDEX vm_synthese_cd_ref_idx ON gn_dashboard.vm_synthese USING btree (cd_ref);
    CREATE UNIQUE INDEX vm_synthese_id_synthese_idx ON gn_dashboard.vm_synthese USING btree (id_synthese);
"""
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW gn_dashboard.vm_taxonomie
    TABLESPACE pg_default
    AS SELECT 'Règne'::text AS level,
        COALESCE(vm_synthese.regne, 'Not defined'::character varying) AS name_taxon
    FROM gn_dashboard.vm_synthese
    GROUP BY vm_synthese.regne
    UNION ALL
    SELECT 'Phylum'::text AS level,
        COALESCE(vm_synthese.phylum, 'Not defined'::character varying) AS name_taxon
    FROM gn_dashboard.vm_synthese
    GROUP BY vm_synthese.phylum
    UNION ALL
    SELECT 'Classe'::text AS level,
        COALESCE(vm_synthese.classe, 'Not defined'::character varying) AS name_taxon
    FROM gn_dashboard.vm_synthese
    GROUP BY vm_synthese.classe
    UNION ALL
    SELECT 'Ordre'::text AS level,
        COALESCE(vm_synthese.ordre, 'Not defined'::character varying) AS name_taxon
    FROM gn_dashboard.vm_synthese
    GROUP BY vm_synthese.ordre
    UNION ALL
    SELECT 'Famille'::text AS level,
        COALESCE(vm_synthese.famille, 'Not defined'::character varying) AS name_taxon
    FROM gn_dashboard.vm_synthese
    GROUP BY vm_synthese.famille
    UNION ALL
    SELECT 'Groupe INPN 1'::text AS level,
        COALESCE(vm_synthese.group1_inpn, 'Not defined'::character varying) AS name_taxon
    FROM gn_dashboard.vm_synthese
    GROUP BY vm_synthese.group1_inpn
    UNION ALL
    SELECT 'Groupe INPN 2'::text AS level,
        COALESCE(vm_synthese.group2_inpn, 'Not defined'::character varying) AS name_taxon
    FROM gn_dashboard.vm_synthese
    GROUP BY vm_synthese.group2_inpn
    UNION ALL
    SELECT 'Groupe INPN 3'::text AS level,
        COALESCE(vm_synthese.group3_inpn, 'Not defined'::character varying) AS name_taxon
    FROM gn_dashboard.vm_synthese
    GROUP BY vm_synthese.group3_inpn
    WITH DATA;
    CREATE UNIQUE INDEX vm_taxonomie_name_taxon_level_idx ON gn_dashboard.vm_taxonomie USING btree (name_taxon, level);
"""
    )
