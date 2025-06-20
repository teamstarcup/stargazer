"""refactor page segments

Revision ID: 4792b5bddfdb
Revises: 9020e29455d1
Create Date: 2025-05-26 18:51:13.557514

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4792b5bddfdb"
down_revision: Union[str, None] = "9020e29455d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "page_segments",
        sa.Column("page_name", sa.String(), nullable=False),
        sa.Column("segment_name", sa.String(), nullable=False),
        sa.Column("segment_hash", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("page_name", "segment_name"),
    )

    # migrate infobox segments
    op.execute(
        """
        INSERT INTO page_segments (page_name, segment_name, segment_hash)
        SELECT concat('Entity:', id), 'Infobox', segment_infobox_hash
        FROM entity_segments;
        """
    )

    # migrate category segments
    op.execute(
        """
        INSERT INTO page_segments (page_name, segment_name, segment_hash)
        SELECT concat('Entity:', id), 'Categories', segment_category_hash
        FROM entity_segments;
        """
    )

    op.drop_table("entity_segments")
    op.drop_table("sprite_segments")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "sprite_segments",
        sa.Column("id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "segment_path_hash", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "segment_license_hash", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "segment_attribution_hash", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("sprite_segments_pkey")),
    )
    op.create_table(
        "entity_segments",
        sa.Column("id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "segment_infobox_hash", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "segment_category_hash", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("entity_segments_pkey")),
    )

    # probably not right, sorry!
    op.execute(
        """
        INSERT INTO entity_segments (id, segment_infobox_hash)
        SELECT replace(id, 'Entity:', ''), segment_hash
        FROM entity_segments
        WHERE segment_name = 'Infobox';
    """
    )

    op.execute(
        """
        INSERT INTO entity_segments (id, segment_category_hash)
        SELECT replace(id, 'Entity:', ''), segment_hash
        FROM entity_segments
        WHERE segment_name = 'Categories';
    """
    )

    op.drop_table("page_segments")
    # ### end Alembic commands ###
