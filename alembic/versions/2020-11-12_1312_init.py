"""init

Revision ID: d136209d4624
Revises: 
Create Date: 2020-11-12 13:12:02.273354

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "d136209d4624"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cameras",
        sa.Column("id", mysql.INTEGER(), nullable=False),
        sa.Column("name", mysql.VARCHAR(length=128), nullable=True),
        sa.Column("url", mysql.VARCHAR(length=128), nullable=True),
        sa.Column("suffix", mysql.VARCHAR(length=128), nullable=True),
        sa.Column("ip_address", mysql.VARCHAR(length=128), nullable=True),
        sa.Column("udp_supported", sa.BOOLEAN(), nullable=True),
        sa.Column("ptz", sa.BOOLEAN(), nullable=True),
        sa.Column("enabled", sa.BOOLEAN(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "configurations",
        sa.Column("id", mysql.INTEGER(), nullable=False),
        sa.Column("name", mysql.VARCHAR(length=128), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "camera_sub_streams",
        sa.Column("id", mysql.INTEGER(), nullable=False),
        sa.Column("camera", mysql.INTEGER(), nullable=True),
        sa.Column("sub_stream", mysql.VARCHAR(length=128), nullable=True),
        sa.ForeignKeyConstraint(["camera"], ["cameras.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cameras_configurations",
        sa.Column("camera_id", mysql.INTEGER(), nullable=False),
        sa.Column("configuration_id", mysql.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["camera_id"],
            ["cameras.id"],
        ),
        sa.ForeignKeyConstraint(
            ["configuration_id"],
            ["configurations.id"],
        ),
        sa.PrimaryKeyConstraint("camera_id", "configuration_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("cameras_configurations")
    op.drop_table("camera_sub_streams")
    op.drop_table("configurations")
    op.drop_table("cameras")
    # ### end Alembic commands ###
