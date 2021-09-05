from . import SubtitleAPI

sub = SubtitleAPI('english', 'farsi/persian')
sub.movie(title='Pi', release_type='bluray').download().extract()
