import React, { useState, useRef } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { CameraView, CameraType, FlashMode, Camera } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import { useNavigation } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS } from '../constants';
import { analyzeImage } from '../services/api';

export default function CameraScreen() {
    const navigation = useNavigation<any>();
    const [facing, setFacing] = useState<CameraType>('back');
    const [flash, setFlash] = useState<FlashMode>('off');
    const [loading, setLoading] = useState(false);
    const cameraRef = useRef<CameraView>(null);

    // Request permissions
    const [permission, requestPermission] = Camera.useCameraPermissions();

    if (!permission) {
        // Camera permissions are still loading
        return <View />;
    }

    if (!permission.granted) {
        // Camera permissions are not granted yet
        return (
            <View style={styles.container}>
                <Text style={styles.message}>We need your permission to show the camera</Text>
                <TouchableOpacity onPress={requestPermission} style={styles.button}>
                    <Text style={styles.text}>Grant Permission</Text>
                </TouchableOpacity>
            </View>
        );
    }

    const toggleCameraFacing = () => {
        setFacing(current => (current === 'back' ? 'front' : 'back'));
    };

    const toggleFlash = () => {
        setFlash(current => (current === 'off' ? 'on' : 'off'));
    };

    const pickImage = async () => {
        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
        });

        if (!result.canceled) {
            processImage(result.assets[0].uri);
        }
    };

    const takePicture = async () => {
        if (cameraRef.current) {
            try {
                const photo = await cameraRef.current.takePictureAsync({
                    quality: 0.8,
                    base64: false,
                });

                if (photo) {
                    processImage(photo.uri);
                }
            } catch (error) {
                Alert.alert("Error", "Failed to take picture");
                console.error(error);
            }
        }
    };

    const processImage = async (uri: string) => {
        setLoading(true);
        try {
            const result = await analyzeImage(uri);
            setLoading(false);
            navigation.navigate('Verify', {
                imageUri: uri,
                detectedText: result.detected_text,
            });
        } catch (error) {
            setLoading(false);
            Alert.alert("Error", "Failed to analyze image. Please try again.");
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            {loading && (
                <View style={styles.loadingOverlay}>
                    <ActivityIndicator size="large" color={COLORS.primary} />
                    <Text style={styles.loadingText}>Analyzing Food...</Text>
                </View>
            )}

            <CameraView
                style={styles.camera}
                facing={facing}
                flash={flash}
                ref={cameraRef}
            >
                <View style={styles.buttonContainer}>
                    <View style={styles.topControls}>
                        <TouchableOpacity style={styles.controlButton} onPress={toggleFlash}>
                            <Text style={styles.text}>{flash === 'on' ? '⚡ On' : '⚡ Off'}</Text>
                        </TouchableOpacity>

                        <TouchableOpacity style={styles.controlButton} onPress={toggleCameraFacing}>
                            <Text style={styles.text}>🔄 Flip</Text>
                        </TouchableOpacity>
                    </View>

                    <View style={styles.bottomControls}>
                        <TouchableOpacity style={styles.galleryButton} onPress={pickImage}>
                            <Text style={styles.text}>🖼️ Gallery</Text>
                        </TouchableOpacity>

                        <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
                            <View style={styles.innerCircle} />
                        </TouchableOpacity>

                        <View style={{ width: 70 }} />
                    </View>
                </View>
            </CameraView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#000',
    },
    message: {
        textAlign: 'center',
        paddingBottom: 10,
        color: 'white',
    },
    camera: {
        flex: 1,
    },
    buttonContainer: {
        flex: 1,
        backgroundColor: 'transparent',
        justifyContent: 'space-between',
        padding: 20,
    },
    topControls: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 20,
    },
    bottomControls: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        alignItems: 'center',
        marginBottom: 30,
    },
    button: {
        alignSelf: 'flex-end',
        alignItems: 'center',
        backgroundColor: COLORS.primary,
        padding: 10,
        borderRadius: 5,
    },
    controlButton: {
        backgroundColor: 'rgba(0,0,0,0.5)',
        padding: 10,
        borderRadius: 20,
    },
    galleryButton: {
        backgroundColor: 'rgba(0,0,0,0.5)',
        padding: 15,
        borderRadius: 30,
    },
    captureButton: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: 'rgba(255,255,255,0.3)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    innerCircle: {
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: 'white',
    },
    text: {
        fontSize: 16,
        fontWeight: 'bold',
        color: 'white',
    },
    loadingOverlay: {
        ...StyleSheet.absoluteFillObject,
        backgroundColor: 'rgba(0,0,0,0.7)',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 100,
    },
    loadingText: {
        color: 'white',
        marginTop: 10,
        fontSize: 18,
        fontWeight: 'bold',
    },
});
