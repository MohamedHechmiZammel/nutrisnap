import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, Image, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, TEST_USER_ID } from '../constants';
import { logMeal } from '../services/api';

type VerifyScreenRouteProp = RouteProp<{
    Verify: { imageUri: string; detectedText: string };
}, 'Verify'>;

export default function VerifyScreen() {
    const route = useRoute<VerifyScreenRouteProp>();
    const navigation = useNavigation<any>();
    const { imageUri, detectedText } = route.params;

    const [description, setDescription] = useState(detectedText);
    const [loading, setLoading] = useState(false);

    const handleConfirm = async () => {
        if (!description.trim()) {
            Alert.alert("Error", "Please enter a description");
            return;
        }

        setLoading(true);
        try {
            const result = await logMeal({
                user_id: TEST_USER_ID,
                verified_text: description,
                image_url: imageUri, // In a real app we'd upload to cloud storage here
            });

            setLoading(false);
            navigation.navigate('Result', { mealLog: result });

        } catch (error) {
            setLoading(false);
            Alert.alert("Error", "Failed to log meal. Please check your connection or simplify the description.");
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollContent}>
                <View style={styles.header}>
                    <Text style={styles.title}>Verify Meal</Text>
                    <Text style={styles.subtitle}>Check the AI detection below</Text>
                </View>

                <Image source={{ uri: imageUri }} style={styles.image} />

                <View style={styles.formContainer}>
                    <Text style={styles.label}>Dish Description</Text>
                    <TextInput
                        style={styles.input}
                        value={description}
                        onChangeText={setDescription}
                        multiline
                        numberOfLines={4}
                        placeholder="E.g., Bowl of Lablabi with tuna..."
                    />
                    <Text style={styles.hint}>
                        Tip: Be specific about portions (e.g., "200g", "1 cup") for better accuracy.
                    </Text>
                </View>

                <TouchableOpacity
                    style={styles.button}
                    onPress={handleConfirm}
                    disabled={loading}
                >
                    {loading ? (
                        <ActivityIndicator color="white" />
                    ) : (
                        <Text style={styles.buttonText}>Confirm & Calculate</Text>
                    )}
                </TouchableOpacity>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    scrollContent: {
        padding: 20,
    },
    header: {
        marginBottom: 20,
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    subtitle: {
        fontSize: 16,
        color: COLORS.textSecondary,
        marginTop: 5,
    },
    image: {
        width: '100%',
        height: 250,
        borderRadius: 15,
        marginBottom: 20,
    },
    formContainer: {
        marginBottom: 30,
    },
    label: {
        fontSize: 16,
        fontWeight: '600',
        color: COLORS.text,
        marginBottom: 10,
    },
    input: {
        backgroundColor: COLORS.card,
        borderRadius: 10,
        padding: 15,
        fontSize: 16,
        minHeight: 100,
        textAlignVertical: 'top',
        borderWidth: 1,
        borderColor: '#E0E0E0',
    },
    hint: {
        fontSize: 14,
        color: COLORS.textSecondary,
        marginTop: 8,
        fontStyle: 'italic',
    },
    button: {
        backgroundColor: COLORS.primary,
        padding: 18,
        borderRadius: 12,
        alignItems: 'center',
        shadowColor: COLORS.primary,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 5,
        elevation: 8,
    },
    buttonText: {
        color: 'white',
        fontSize: 18,
        fontWeight: 'bold',
    },
});
