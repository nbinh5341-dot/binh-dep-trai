local Players = game:GetService("Players")
local LocalPlayer = Players.LocalPlayer
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local TextChatService = game:GetService("TextChatService")
local ChatRemote = ReplicatedStorage:FindFirstChild("DefaultChatSystemChatEvents") and ReplicatedStorage.DefaultChatSystemChatEvents:FindFirstChild("SayMessageRequest")

local function sendChatMessage(message)
    -- Thử gửi bằng hệ thống TextChatService mới
    if TextChatService and TextChatService.ChatVersion == Enum.ChatVersion.TextChatService then
        local channels = TextChatService:FindFirstChild("TextChannels")
        if channels and channels:FindFirstChild("RBXGeneral") then
            channels.RBXGeneral:SendAsync(message)
        end
    -- Thử gửi bằng hệ thống Chat cũ
    elseif ChatRemote then
        ChatRemote:FireServer(message, "All")
    end
end

local function startSpamming()
    while true do
        sendChatMessage("ez")
        
        -- Chờ 2 giây giữa mỗi lần chat để không bị Roblox chặn chat (văng chat)
        task.wait(2.0) 
    end
end

task.spawn(startSpamming)
