from time import sleep

from onvif import ONVIFCamera


class PTZ(object):
    def __init__(self):
        self.mycam = ONVIFCamera("192.168.0.53", 80, "admin", "AGHspace")

        self.media = self.mycam.create_media_service()
        self.media_profile = self.media.GetProfiles()[0]
        self.ptz = self.mycam.create_ptz_service()

        request = self.ptz.create_type("GetConfigurationOptions")
        request.ConfigurationToken = self.media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        self.continuous_move = self.ptz.create_type("ContinuousMove")
        self.continuous_move.ProfileToken = self.media_profile.token

        self.continuous_move.Velocity = self.ptz.GetStatus(
            {"ProfileToken": self.media_profile.token}
        ).Position

        self.continuous_move.Velocity.PanTilt.space = (
            ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
        )
        self.continuous_move.Velocity.Zoom.space = (
            ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI
        )

        self.XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[
            0
        ].XRange.Max
        self.XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[
            0
        ].XRange.Min
        self.YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[
            0
        ].YRange.Max
        self.YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[
            0
        ].YRange.Min

    def perform_move(self, timeout):
        self.ptz.ContinuousMove(self.continuous_move)
        sleep(timeout)
        self.ptz.Stop({"ProfileToken": self.continuous_move.ProfileToken})

    def move_up(self, timeout=0.25):
        print("move up...")
        self.continuous_move.Velocity.PanTilt.x = 0
        self.continuous_move.Velocity.PanTilt.y = self.YMAX
        self.perform_move(timeout)

    def move_down(self, timeout=0.25):
        print("move down...")
        self.continuous_move.Velocity.PanTilt.x = 0
        self.continuous_move.Velocity.PanTilt.y = self.YMIN
        self.perform_move(timeout)

    def move_right(self, timeout=0.25):
        print("move right...")
        self.continuous_move.Velocity.PanTilt.x = self.XMAX
        self.continuous_move.Velocity.PanTilt.y = 0
        self.perform_move(timeout)

    def move_left(self, timeout=0.25):
        print("move left...")
        self.continuous_move.Velocity.PanTilt.x = self.XMIN
        self.continuous_move.Velocity.PanTilt.y = 0
        self.perform_move(timeout)
