"""empty message

Revision ID: 111cdeafea2e
Revises: fa911eb4e6d0
Create Date: 2020-08-25 18:20:02.297918

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '111cdeafea2e'
down_revision = 'fa911eb4e6d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('genreId', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('PodCast',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artistName', sa.String(), nullable=True),
    sa.Column('podCastId', sa.Integer(), nullable=True),
    sa.Column('releaseDate', sa.Date(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('kind', sa.String(), nullable=True),
    sa.Column('copyright', sa.String(), nullable=True),
    sa.Column('artistId', sa.Integer(), nullable=True),
    sa.Column('contentAdvisoryRating', sa.String(), nullable=True),
    sa.Column('artistUrl', sa.String(), nullable=True),
    sa.Column('artworkUrl100', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.Binary(), nullable=True),
    sa.Column('access', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('User')
    op.drop_table('PodCast')
    op.drop_table('Genre')
    # ### end Alembic commands ###