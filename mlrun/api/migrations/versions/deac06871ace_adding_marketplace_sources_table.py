"""Adding marketplace sources table

Revision ID: deac06871ace
Revises: e1dd5983c06b
Create Date: 2021-06-30 15:56:09.543139

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "deac06871ace"
down_revision = "e1dd5983c06b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "marketplace_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("index", sa.Integer(), nullable=True),
        sa.Column("created", sa.TIMESTAMP(), nullable=True),
        sa.Column("updated", sa.TIMESTAMP(), nullable=True),
        sa.Column("object", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="_marketplace_sources_uc"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("marketplace_sources")
    # ### end Alembic commands ###
